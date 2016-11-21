from django.shortcuts import render

from django.contrib.auth.views import login
from .forms import RegisterForm,LoginForm
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


# Create your views here.
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

    def form_valid(self, form):
        user = form.save(False)

        user.save(True)
        return HttpResponseRedirect('/')


class LoginView(FormView):
    form_class =LoginForm
    template_name = 'account/login.html'
