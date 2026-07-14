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
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.utils.http import url_has_allowed_host_and_scheme

from djangoblog.blog_signals import oauth_user_login_signal
from djangoblog.utils import get_current_site
from djangoblog.utils import send_email, get_sha256
from oauth.forms import RequireEmailForm
from oauth.state_manager import generate_oauth_state, validate_oauth_state
from .models import OAuthUser
from .oauthmanager import get_manager_by_type, OAuthAccessTokenException

logger = logging.getLogger(__name__)


def get_redirecturl(request):
    nexturl = request.GET.get('next_url', None)
    if not nexturl or nexturl == '/login/' or nexturl == '/login':
        return '/'

    # Only allow relative URLs or URLs pointing to the current host
    site_domain = get_current_site().domain
    if url_has_allowed_host_and_scheme(
        url=nexturl,
        allowed_hosts={site_domain},
        require_https=request.is_secure()
    ):
        return nexturl

    logger.info('非法url:' + str(nexturl))
    return '/'


def oauthlogin(request):
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    
    # Generate and store OAuth state for CSRF protection
    state = generate_oauth_state(request.session.session_key, type)
    
    nexturl = get_redirecturl(request)
    authorizeurl = manager.get_authorization_url(nexturl, state)
    return HttpResponseRedirect(authorizeurl)


def authorize(request):
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    
    # Validate OAuth state parameter for CSRF protection
    state = request.GET.get('state', None)
    if not request.session.session_key or not validate_oauth_state(request.session.session_key, type, state):
        logger.warning(f"Invalid OAuth state parameter for type: {type}")
        return HttpResponseForbidden(_("Invalid OAuth state parameter. Possible CSRF attack."))
    
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
        # Regenerate state for retry
        state = generate_oauth_state(request.session.session_key, type)
        return HttpResponseRedirect(manager.get_authorization_url(nexturl, state))
    user = manager.get_oauth_userinfo()
    if user:
        if not user.nickname or not user.nickname.strip():
            user.nickname = "djangoblog" + timezone.now().strftime('%y%m%d%I%M%S')
        
        # facebook的token过长
        if type == 'facebook':
            user.token = ''
        
        # Use atomic get_or_create to avoid race conditions
        with transaction.atomic():
            oauth_user, created = OAuthUser.objects.get_or_create(
                type=type,
                openid=user.openid,
                defaults={
                    'nickname': user.nickname,
                    'token': user.token,
                    'picture': user.picture,
                    'email': user.email,
                    'metadata': user.metadata
                }
            )
            if not created:
                # Update existing OAuth user
                oauth_user.picture = user.picture
                oauth_user.metadata = user.metadata
                oauth_user.nickname = user.nickname
                oauth_user.token = user.token
                if user.email:
                    oauth_user.email = user.email
                oauth_user.save()
            
            user = oauth_user
        
        if user.author_id:
            # OAuth user is already linked to an account
            with transaction.atomic():
                try:
                    author = get_user_model().objects.get(pk=user.author_id)
                    # Check if user account is active
                    if not author.is_active:
                        logger.warning(f"Attempt to login with inactive account: {author.username}")
                        return HttpResponseForbidden(_("Your account has been deactivated."))
                    
                    oauth_user_login_signal.send(
                        sender=authorize.__class__, id=user.id)
                    login(request, author)
                    # 设置session过期时间为2周（默认）
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    # 设置登录标记 cookie
                    response = HttpResponseRedirect(nexturl)
                    response.set_cookie(
                        'logged_user',
                        'true',
                        max_age=settings.SESSION_COOKIE_AGE,
                        httponly=False,  # 允许 JavaScript 访问
                        samesite='Lax'
                    )
                    return response
                except ObjectDoesNotExist:
                    # Author was deleted, need to re-bind
                    pass
        
        # OAuth user is not linked yet, redirect to email binding page
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
                author.username = oauthuser.nickname.strip() if oauthuser.nickname.strip(
                ) else "djangoblog" + timezone.now().strftime('%y%m%d%I%M%S')
                author.save()
        oauthuser.author = author
        oauthuser.save()
    
    # Check if user account is active before allowing login
    if not author.is_active:
        logger.warning(f"Attempt to login with inactive account via email confirmation: {author.username}")
        return HttpResponseForbidden(_("Your account has been deactivated."))
    
    oauth_user_login_signal.send(
        sender=emailconfirm.__class__,
        id=oauthuser.id)
    login(request, author)
    # 设置session过期时间为2周（默认）
    request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    site = 'http://' + get_current_site().domain
    content = _('''
     <p>Congratulations, you have successfully bound your email address. You can use
      %(oauthuser_type)s to directly log in to this website without a password.</p>
       You are welcome to continue to follow this site, the address is
        <a href="%(site)s" rel="bookmark">%(site)s</a>
            Thank you again!
            <br />
        If the link above cannot be opened, please copy this link to your browser.
        %(site)s
    ''') % {'oauthuser_type': oauthuser.type, 'site': site}

    send_email(emailto=[oauthuser.email, ], title=_('Congratulations on your successful binding!'), content=content)
    url = reverse('oauth:bindsuccess', kwargs={
        'oauthid': id
    })
    url = url + '?type=success'
    # 设置登录标记 cookie
    response = HttpResponseRedirect(url)
    response.set_cookie(
        'logged_user',
        'true',
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=False,  # 允许 JavaScript 访问
        samesite='Lax'
    )
    return response


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
        return {
            'email': ''
        }

    def get_context_data(self, **kwargs):
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        if oauthuser.picture:
            kwargs['picture'] = oauthuser.picture
        return super(RequireEmailView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Get oauthid from URL, not from form data to prevent IDOR
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        
        # Validate that OAuth user is not already linked to prevent account takeover
        if oauthuser.author_id:
            logger.warning(f"Attempt to rebind already linked OAuth user: {oauthid}")
            return HttpResponseForbidden(_("This OAuth account is already bound to an account."))
        
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

        content = _("""
               <p>Please click the link below to bind your email</p>

                 <a href="%(url)s" rel="bookmark">%(url)s</a>

                 Thank you again!
                 <br />
                 If the link above cannot be opened, please copy this link to your browser.
                  <br />
                 %(url)s
                """) % {'url': url}
        send_email(emailto=[email, ], title=_('Bind your email'), content=content)
        url = reverse('oauth:bindsuccess', kwargs={
            'oauthid': oauthid
        })
        url = url + '?type=email'
        return HttpResponseRedirect(url)


def bindsuccess(request, oauthid):
    type = request.GET.get('type', None)
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if type == 'email':
        title = _('Bind your email')
        content = _(
            'Congratulations, the binding is just one step away. '
            'Please log in to your email to check the email to complete the binding. Thank you.')
    else:
        title = _('Binding successful')
        content = _(
            "Congratulations, you have successfully bound your email address. You can use %(oauthuser_type)s"
            " to directly log in to this website without a password. You are welcome to continue to follow this site." % {
                'oauthuser_type': oauthuser.type})
    return render(request, 'oauth/bindsuccess.html', {
        'title': title,
        'content': content
    })
