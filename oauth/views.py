import logging
# Create your views here.
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView

from djangoblog.blog_signals import oauth_user_login_signal
from djangoblog.utils import get_current_site
from djangoblog.utils import send_email, get_sha256
from oauth.forms import RequireEmailForm
from .models import OAuthUser
from .oauthmanager import get_manager_by_type, OAuthAccessTokenException

logger = logging.getLogger(__name__)


def get_redirecturl(request):
    nexturl = request.GET.get('next_url', None)
    if not nexturl or nexturl == '/login/' or nexturl == '/login':
        nexturl = '/'
        return nexturl
    p = urlparse(nexturl)
    if p.netloc:
        site = get_current_site().domain
        if not p.netloc.replace('www.', '') == site.replace('www.', ''):
            logger.info('非法url:' + nexturl)
            return "/"
    return nexturl


def oauthlogin(request):
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    nexturl = get_redirecturl(request)
    authorizeurl = manager.get_authorization_url(nexturl)
    return HttpResponseRedirect(authorizeurl)


def authorize(request):
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    code = request.GET.get('code', None)
    try:
        rsp = manager.get_access_token_by_code(code)
    except OAuthAccessTokenException as e:
        logger.warning("OAuthAccessTokenException:" + str(e))
        return HttpResponseRedirect('/')
    except Exception as e:
        logger.error(e)
        rsp = None
    nexturl = get_redirecturl(request)
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url(nexturl))
    user = manager.get_oauth_userinfo()
    if user:
        if not user.nikename or not user.nikename.strip():
            user.nikename = "djangoblog" + timezone.now().strftime('%y%m%d%I%M%S')
        try:
            temp = OAuthUser.objects.get(type=type, openid=user.openid)
            temp.picture = user.picture
            temp.matedata = user.matedata
            temp.nikename = user.nikename
            user = temp
        except ObjectDoesNotExist:
            pass
        # facebook的token过长
        if type == 'facebook':
            user.token = ''
        if user.email:
            with transaction.atomic():
                author = None
                try:
                    author = get_user_model().objects.get(id=user.author_id)
                except ObjectDoesNotExist:
                    pass
                if not author:
                    result = get_user_model().objects.get_or_create(email=user.email)
                    author = result[0]
                    if result[1]:
                        try:
                            get_user_model().objects.get(username=user.nikename)
                        except ObjectDoesNotExist:
                            author.username = user.nikename
                        else:
                            author.username = "djangoblog" + timezone.now().strftime('%y%m%d%I%M%S')
                        author.source = 'authorize'
                        author.save()

                user.author = author
                user.save()

                oauth_user_login_signal.send(
                    sender=authorize.__class__, id=user.id)
                login(request, author)
                return HttpResponseRedirect(nexturl)
        else:
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
    if not get_sha256(settings.SECRET_KEY +
                      str(id) +
                      settings.SECRET_KEY).upper() == sign.upper():
        return HttpResponseForbidden()
    oauthuser = get_object_or_404(OAuthUser, pk=id)
    with transaction.atomic():
        if oauthuser.author:
            author = get_user_model().objects.get(pk=oauthuser.author_id)
        else:
            result = get_user_model().objects.get_or_create(email=oauthuser.email)
            author = result[0]
            if result[1]:
                author.source = 'emailconfirm'
                author.username = oauthuser.nikename.strip() if oauthuser.nikename.strip(
                ) else "djangoblog" + timezone.now().strftime('%y%m%d%I%M%S')
                author.save()
        oauthuser.author = author
        oauthuser.save()
    oauth_user_login_signal.send(
        sender=emailconfirm.__class__,
        id=oauthuser.id)
    login(request, author)

    site = get_current_site().domain
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
        sign = get_sha256(settings.SECRET_KEY +
                          str(oauthuser.id) + settings.SECRET_KEY)
        site = get_current_site().domain
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
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if type == 'email':
        title = '绑定成功'
        content = "恭喜您，还差一步就绑定成功了，请登录您的邮箱查看邮件完成绑定，谢谢。"
    else:
        title = '绑定成功'
        content = "恭喜您绑定成功，您以后可以使用{type}来直接免密码登录本站啦，感谢您对本站对关注。".format(
            type=oauthuser.type)
    return render(request, 'oauth/bindsuccess.html', {
        'title': title,
        'content': content
    })
