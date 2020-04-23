#!/usr/bin/env python

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import widgets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "логин или email",
                                                                  "class": "input_creds", "autocomplete": "off", "autofocus":"",
                                                                  "style": "background-repeat: no-repeat; background-attachment: scroll; background-size: 16px 18px; background-position: 98% 50%; cursor: pointer; background-image: none;"})
        self.fields['username'].label = ""
        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': "пароль", "class": "input_creds", "name": "pass", "autocomplete": "off"})
        self.fields['password'].span = ""


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "логин", "class": "input_creds", "autocomplete": "off", "autofocus":""})
        self.fields['username'].label = "логин"
        self.fields['email'].widget = widgets.EmailInput(attrs={'placeholder': "email", "class": "input_creds", "autocomplete": "off"})
        self.fields['email'].label = "email"
        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': "пароль", "class": "input_creds"})
        self.fields['password1'].label = "пароль"
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': "пароль еще раз", "class": "input_creds"})
        self.fields['password2'].label = "пароль еще раз"

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Такой email адрес уже зарегистрирован.")
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
