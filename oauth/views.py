from django.shortcuts import render

# Create your views here.
from urllib.parse import urlparse
import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from .models import OAuthUser
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, RedirectView
from oauth.forms import RequireEmailForm
from django.urls import reverse
from django.db import transaction
from DjangoBlog.utils import send_email, get_md5, save_user_avatar
from DjangoBlog.utils import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from .oauthmanager import get_manager_by_type, OAuthAccessTokenException
from DjangoBlog.blog_signals import oauth_user_login_signal

import logging

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
            import datetime
            user.nikename = "djangoblog" + datetime.datetime.now().strftime('%y%m%d%I%M%S')
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
                        author.username = user.nikename
                        author.source = 'authorize'
                        author.save()

                user.author = author
                user.save()

                oauth_user_login_signal.send(sender=authorize.__class__, id=user.id)
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
    if not get_md5(settings.SECRET_KEY + str(id) + settings.SECRET_KEY).upper() == sign.upper():
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
                author.username = oauthuser.nikename.strip() if oauthuser.nikename.strip() else "djangoblog" + datetime.datetime.now().strftime(
                    '%y%m%d%I%M%S')
                author.save()
        oauthuser.author = author
        oauthuser.save()
    oauth_user_login_signal.send(sender=emailconfirm.__class__, id=oauthuser.id)
    login(request, author)

    site = get_current_site().domain
    content = '''
     <p>Ура，привязали ящик с почтой. Используй {type}, чтобы не вводить паролей.</p>
     Моя идея в двух словах:

            Я топлю за то, что нет ничего правдивее твоих личных историй из жизни, которые изменили твое отношение к чему-то. Я убежден, что в конечном счете все эти истории в некоторой абстракции похожи. Мы все переживаем одни и те же потрясения. И совершенно круто ими делиться. Неважно, обосрался ты по полной или наоборот пришел и выебал все эти хит-парады. А еще круто уметь смеяться над собой, но не проебать грань. И хорошо относиться друг к другу - подъебывать качественно.

            !!! Я презираю безосновательную критику чужого субъективного. Чужие вкусы надо пытаться понять. Однажды это может неплохо пригодиться. Мы очень разные. Из этого нужно брать пользу.
            !!! Никакой нахуй озлобленной печальной хуйни!!! Я топлю за позитивное мышление, даже если ты умираешь, радуйся за тех, кому остается больше воздуха. Радуйся, что ты больше этих тварей не увидишь!
            !!! Если чья-то мысль может быть двояко истолкована, ты выбираешь всегда хороший вариант. Пробуешь прочитать с разной интонацией. Пробуешь. Если надо уточняешь. Нахуй недопонимания.

            Мы тут любим истории. Любое мнение становится пиздатым, когда с ним связана история, переживания, умственная работа.

                <p>А теперь давай жмякай на ссыль</p>

                <a href="{url}" rel="bookmark">{url}</a>


                <br />
                Если ссылка не открывается, копируй руками:
                {url}
    '''.format(type=oauthuser.type, url='http://' + site)

    send_email(emailto=[oauthuser.email, ], title='Ура!', content=content)
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
        site = get_current_site().domain
        if settings.DEBUG:
            site = '127.0.0.1:8000'
        path = reverse('oauth:email_confirm', kwargs={
            'id': oauthid,
            'sign': sign
        })
        url = "http://{site}{path}".format(site=site, path=path)

        content = """
                <p>Жми на ссылку, чтобы привязать свой почтовый ящик:</p>

                <a href="{url}" rel="bookmark">{url}</a>
                <br />
                Если ссылка не открывается, копируй руками:
                {url}
                """.format(url=url)
        send_email(emailto=[email, ], title='Привязать свой почтовый ящик', content=content)
        url = reverse('oauth:bindsuccess', kwargs={
            'oauthid': oauthid
        })
        url = url + '?type=email'
        return HttpResponseRedirect(url)


def bindsuccess(request, oauthid):
    type = request.GET.get('type', None)
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if type == 'email':
        title = 'Привязали успешно'
        content = "Осталось немного! Логинься в почту и жмякай ссыль для подтверждения!"
    else:
        title = 'Привязали успешно'
        content = "Ура，привязали ящик с почтой. Используй {type}, чтобы не вводить паролей.".format(type=oauthuser.type)
    return render(request, 'oauth/bindsuccess.html', {
        'title': title,
        'content': content
    })
