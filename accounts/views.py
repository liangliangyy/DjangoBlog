from django.shortcuts import render
import logging
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
# from django.views.generic.edit import FormView
from django.views.generic import FormView, RedirectView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
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
from DjangoBlog.utils import send_email, get_md5, get_current_site
from django.conf import settings

logger = logging.getLogger(__name__)


# Create your views here.

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

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

            content = """
                            <p>Пожалуйста, подтвердите почтовый адрес переходом по ссылке</p>

                            <a href="{url}" rel="bookmark">{url}</a>

                            <br />
                            Если ссылка выше не открывается，то копируй руками:。
                            {url}
                            """.format(url=url)
            send_email(emailto=[user.email, ], title='Verify your email', content=content)

            url = reverse('accounts:result') + '?type=register&id=' + str(user.id)
            return HttpResponseRedirect(url)
        else:
            return self.render_to_response({
                'form': form
            })


class LogoutView(RedirectView):
    url = '/login/'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from DjangoBlog.utils import cache
        cache.clear()
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class LoginView(FormView):
    form_class = LoginForm
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
        kwargs['redirect_to'] = redirect_to

        return super(LoginView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            from DjangoBlog.utils import cache
            if cache and cache is not None:
                cache.clear()
            logger.info(self.redirect_field_name)

            auth.login(self.request, form.get_user())
            return super(LoginView, self).form_valid(form)
            # return HttpResponseRedirect('/')
        else:
            return self.render_to_response({
                'form': form
            })

    def get_success_url(self):

        redirect_to = self.request.POST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
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
    Круто, что ты с нами! Подтверждай свою почту {email}
    '''.format(email=user.email)
            title = 'Регистрация прошла успешно'
        else:
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '''
            Почта подтверждена! Моя идея в двух словах:

            Я топлю за то, что нет ничего правдивее твоих личных историй из жизни, которые изменили твое отношение к чему-то. Я убежден, что в конечном счете все эти истории в некоторой абстракции похожи. Мы все переживаем одни и те же потрясения. И совершенно круто ими делиться. Неважно, обосрался ты по полной или наоборот пришел и выебал все эти хит-парады. А еще круто уметь смеяться над собой, но не проебать грань. И хорошо относиться друг к другу - подъебывать качественно.

            !!! Я презираю безосновательную критику чужого субъективного. Чужие вкусы надо пытаться понять. Однажды это может неплохо пригодиться. Мы очень разные. Из этого нужно брать пользу.
            !!! Никакой нахуй озлобленной печальной хуйни!!! Я топлю за позитивное мышление, даже если ты умираешь, радуйся за тех, кому остается больше воздуха. Радуйся, что ты больше этих тварей не увидишь!
            !!! Если чья-то мысль может быть двояко истолкована, ты выбираешь всегда хороший вариант. Пробуешь прочитать с разной интонацией. Пробуешь. Если надо уточняешь. Нахуй недопонимания.

            Мы тут любим истории. Любое мнение становится пиздатым, когда с ним связана история, переживания, умственная работа.
            '''
            title = 'Почта подтверждена'
        return render(request, 'account/result.html', {
            'title': title,
            'content': content
        })
    else:
        return HttpResponseRedirect('/')
