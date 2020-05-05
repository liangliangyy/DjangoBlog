from django.shortcuts import render
import logging
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
# from django.views.generic.edit import FormView
from django.views.generic import FormView, RedirectView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import is_safe_url
from DjangoBlog.utils import send_email, get_md5, get_current_site, render_template
from django.conf import settings
from django.contrib import messages
import json
from django.http import JsonResponse
logger = logging.getLogger(__name__)


# Create your views here.

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

    def form_invalid(self, form):
        for field, errors in form.errors.as_data().items():
            for error in errors:
                messages.add_message(self.request, messages.ERROR, ' '.join(error))
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)
            site = get_current_site().domain
            sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))

            if settings.DEBUG:
                site = '127.0.0.1:8000'
            path = reverse('account:result')
            url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(site=site, path=path, id=user.id,
                                                                                   sign=sign)
            content = render_template('confirm_email.j2', vars=locals())
            subject = 'Подтвердите email адрес'
            if content is not None:
                send_email(emailto=[user.email, ],
                           title=subject,
                           content=content,
                           images={"logo.png": "image/png", "mail_icon.png": "image/png"})

            url = reverse('accounts:result') + '?type=register&id=' + str(user.id)
            messages.success(self.request, f"Новый аккаунт %s создан. Подтвердите свой почтовый ящик: %s" % (user.username, user.email))
            return HttpResponseRedirect(url)
        else:
            messages.error(self.request, form.errors)
            return self.render_to_response({
                'form': form
            })


class LogoutView(RedirectView):
    url = '/'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from DjangoBlog.utils import cache
        cache.clear()
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class CustomAuthForm(LoginForm):
    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = 'Неверное имя пользователя или пароль'
        super().__init__(*args, **kwargs)


class LoginView(FormView):
    form_class = CustomAuthForm
    template_name = 'account/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME


    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if redirect_to is None:
            redirect_to = '/'
        logger.info("redirect_to: {}".format(redirect_to))
        kwargs['redirect_to'] = redirect_to
        return super(LoginView, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        form_errors = []
        for field, error_list in form.errors.as_data().items():
            form_errors = [error.message for error in error_list]

        if self.request.is_ajax():
            logger.info("ajax failed login request")
            # logger.info("\n".join(form_errors))
            return JsonResponse({"message": "Failure", 'errors': "\n".join(form_errors)}, content_type="application/json")

        for error in form_errors:
            messages.add_message(self.request, messages.ERROR, ''.join(error))
        return super().form_invalid(form)


    def form_valid(self, form):
        form = CustomAuthForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            from DjangoBlog.utils import cache
            if cache and cache is not None:
                cache.clear()

            auth.login(self.request, form.get_user())
            if self.request.is_ajax():
                logger.info("ajax succesfull login request")
                return JsonResponse({"message": "Success"}, content_type="application/json")

            return super(LoginView, self).form_valid(form)
        else:
            messages.error(self.request, form.errors)
            return self.render_to_response({
                'form': form
            })

    def get_success_url(self):
        redirect_to = self.request.POST.get(self.redirect_field_name)
        logging.info("redirect_to: {}".format(redirect_to))
        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            messages.error(self.request, 'Неверное имя пользователя или пароль')
            redirect_to = self.success_url
        return redirect_to


def account_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)
    if user.is_active:
        return HttpResponseRedirect('/')
    if type and type in ['register', 'validation']:
        if type == 'register':
            content = '''
    Круто, что ты с нами! Осталось подтвердить указанный почтовый ящик {email}
    '''.format(email=user.email)
            title = 'Регистрация прошла успешно'
        else:
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            messages.success(request, 'Почта успешно подтверждена!')
        return HttpResponseRedirect('/')
