from django.shortcuts import render

# Create your views here.
from .oauthmanager import WBOauthManager, GoogleOauthManager, get_manager_by_type
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from .models import OAuthUser
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, RedirectView
from oauth.forms import RequireEmailForm
from django.core.urlresolvers import reverse


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
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url())
    user = manager.get_oauth_userinfo()
    author = None
    if user:
        email = user.email
        email = None
        if email:
            author = get_user_model().objects.get(email=email)
            if not author:
                author = get_user_model().objects.create_user(username=user.nikename, email=email)
            user.author = author
            user.save()
            login(request, author)
            return HttpResponseRedirect('/')
        if not email:
            author = get_user_model().objects.create_user(username=user.nikename)
            user.author = author
            user.save()
            url = reverse('oauth:require_email', kwargs=
            {
                'oauthid': user.id
            })
            print(url)
            return HttpResponseRedirect(url)


"""
def require_email(request, oauthid):
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if oauthuser.email:
        return HttpResponseRedirect('/')

"""


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
        from DjangoBlog.utils import send_email
        url = '123'
        content = """
                <p>请点击下面链接绑定您的邮箱</p>

                <a href="{url}" rel="bookmark">{url}</a>

                再次感谢您！
                <br />
                如果上面链接无法打开，请将此链接复制至浏览器。
                {url}
                """.format(url=url)
        send_email('绑定您的电子邮箱', content, [email, ])
        return HttpResponseRedirect('/')


"""
def wbauthorize(request, sitename):
    manager = WBOauthManager(client_id=settings.OAHUTH['sina']['appkey'],
                             client_secret=settings.OAHUTH['sina']['appsecret'],
                             callback_url=settings.OAHUTH['sina']['callbackurl'])
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    print(rsp)
    return HttpResponse(rsp)


def wboauthurl(request):
    manager = WBOauthManager(client_id=settings.OAHUTH['sina']['appkey'],
                             client_secret=settings.OAHUTH['sina']['appsecret'],
                             callback_url=settings.OAHUTH['sina']['callbackurl'])
    url = manager.get_authorization_url()
    return HttpResponse(url)


def googleoauthurl(request):
    manager = GoogleOauthManager()
    url = manager.get_authorization_url()
    return HttpResponse(url)


def googleauthorize(request):
    manager = GoogleOauthManager()
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url())
    user = manager.get_oauth_userinfo()
    if user:
        email = user['email']
        if email:
            author = get_user_model().objects.get(email=email)
            if not author:
                author = get_user_model().objects.create_user(username=user["name"], email=email)
            if not GoogleUserInfo.objects.filter(author_id=author.pk):
                userinfo = GoogleUserInfo()
                userinfo.author = author
                userinfo.picture = user["picture"]
                userinfo.token = manager.access_token
                userinfo.openid = manager.openid
                userinfo.nikename = user["name"]
                userinfo.save()
            login(request, author)
        else:
            pass
    return HttpResponseRedirect('/')
"""
