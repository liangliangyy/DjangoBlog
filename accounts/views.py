from django.shortcuts import render

from django.contrib.auth.views import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import auth
from django.views.decorators.cache import never_cache


# Create your views here.

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

    def form_valid(self, form):
        user = form.save(False)

        user.save(True)
        return HttpResponseRedirect('/')


def LogOut(requests):
    logout(request=requests)
    return HttpResponseRedirect("/")


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            # login(self.request, form.get_user())
            auth.login(self.request, form.get_user())

            return HttpResponseRedirect('/')
        else:
            return self.render_to_response({
                'form': form
            })
