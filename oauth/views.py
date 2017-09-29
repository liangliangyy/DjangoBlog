from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from .models import OAuthUser
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, RedirectView
from oauth.forms import RequireEmailForm
from django.core.urlresolvers import reverse
from DjangoBlog.utils import send_email, get_md5
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from .oauthmanager import get_manager_by_type


def oauthlogin(request):
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    nexturl = request.GET.get('next_url', None)
    print(nexturl)
    if not nexturl or nexturl == '/login/':
        nexturl = '/'
    authorizeurl = manager.get_authorization_url(nexturl)
    return HttpResponseRedirect(authorizeurl)


def authorize(request):
    manager = None
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    nexturl = request.GET.get('next_url', None)
    if not nexturl:
        nexturl = '/'
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url(nexturl))
    user = manager.get_oauth_userinfo()

    if user:
        if not user.nikename:
            import datetime
            user.nikename = "djangoblog" + datetime.datetime.now().strftime('%y%m%d%I%M%S')
        try:
            token = user.token
            user = OAuthUser.objects.get(type=type, openid=user.openid)
            if token:
                user.token = token
        except ObjectDoesNotExist:
            pass
        email = user.email
        if email:
            author = None
            try:
                author = get_user_model().objects.get(id=user.author_id)
            except ObjectDoesNotExist:
                pass
            if not author:
                result = get_user_model().objects.get_or_create(email=user.email)
                author = result[0]
                if result[1]:
                    author.username = user.nikename
                    author.save()

            user.author = author
            user.save()
            login(request, author)
            return HttpResponseRedirect(nexturl)
        if not email:
            user.save()
            url = reverse('oauth:require_email', kwargs={
                'oauthid': user.id
            })

            return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(nexturl)


def emailconfirm(request, id, sign):
    if not sign:
        return HttpResponseForbidden()
    if not get_md5(settings.SECRET_KEY + str(id) + settings.SECRET_KEY).upper() == sign.upper():
        return HttpResponseForbidden()
    oauthuser = get_object_or_404(OAuthUser, pk=id)
    author = None
    if oauthuser.author:
        author = get_user_model().objects.get(pk=oauthuser.author_id)
    else:
        result = get_user_model().objects.get_or_create(email=oauthuser.email)
        author = result[0]
        if result[1]:
            author.username = oauthuser.nikename
            author.save()
    """
    if oauthuser.email and author.email:
        login(request, author)
        return HttpResponseRedirect('/')
    """
    oauthuser.author = author
    oauthuser.save()
    login(request, author)

    site = Site.objects.get_current().domain
    content = '''
     <p>恭喜您，您已经成功绑定您的邮箱，您可以使用{type}来直接免密码登录本网站.欢迎您继续关注本站，地址是</p>

                <a href="{url}" rel="bookmark">{url}</a>

                再次感谢您！
                <br />
                如果上面链接无法打开，请将此链接复制至浏览器。
                {url}
    '''.format(type=oauthuser.type, url='http://' + site)

    send_email(emailto=[oauthuser.email, ], title='恭喜您绑定成功!', content=content)
    url = reverse('oauth:bindsuccess', kwargs={
        'oauthid': id
    })
    url = url + '?type=success'
    return HttpResponseRedirect(url)


class RequireEmailView(FormView):
    form_class = RequireEmailForm
    template_name = 'oauth/require_email.html'

    def get(self, request, *args, **kwargs):
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        if oauthuser.email:
            pass
            # return HttpResponseRedirect('/')

        return super(RequireEmailView, self).get(request, *args, **kwargs)

    def get_initial(self):
        oauthid = self.kwargs['oauthid']
        return {
            'email': '',
            'oauthid': oauthid
        }

    def get_context_data(self, **kwargs):
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        if oauthuser.picture:
            kwargs['picture'] = oauthuser.picture
        return super(RequireEmailView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        oauthid = form.cleaned_data['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        oauthuser.email = email
        oauthuser.save()
        sign = get_md5(settings.SECRET_KEY + str(oauthuser.id) + settings.SECRET_KEY)
        site = Site.objects.get_current().domain
        if settings.DEBUG:
            site = '127.0.0.1:8000'
        path = reverse('oauth:email_confirm', kwargs={
            'id': oauthid,
            'sign': sign
        })
        url = "http://{site}{path}".format(site=site, path=path)

        content = """
                <p>请点击下面链接绑定您的邮箱</p>

                <a href="{url}" rel="bookmark">{url}</a>

                再次感谢您！
                <br />
                如果上面链接无法打开，请将此链接复制至浏览器。
                {url}
                """.format(url=url)
        send_email(emailto=[email, ], title='绑定您的电子邮箱', content=content)
        url = reverse('oauth:bindsuccess', kwargs={
            'oauthid': oauthid
        })
        url = url + '?type=email'
        return HttpResponseRedirect(url)


def bindsuccess(request, oauthid):
    type = request.GET.get('type', None)

    title = ''
    content = ''
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if type == 'email':
        title = '绑定成功'
        content = "恭喜您，还差一步就绑定成功了，请登录您的邮箱查看邮件完成绑定，谢谢。"
    else:
        title = '绑定成功'
        content = "恭喜您绑定成功，您以后可以使用{type}来直接免密码登录本站啦，感谢您对本站对关注。".format(type=oauthuser.type)
    return render(request, 'oauth/bindsuccess.html', {
        'title': title,
        'content': content
    })
