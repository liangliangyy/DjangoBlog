#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: urls.py
@time: 2016/11/20 下午3:52
"""

from django.conf.urls import url
from django.contrib.auth import views as auth_view
from django.urls import path
from . import views
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [url(r'^login/$',
                   views.LoginView.as_view(success_url='/'),
                   name='login',
                   kwargs={'authentication_form': LoginForm}),
               url(r'^register/$',
                   views.RegisterView.as_view(success_url="/"),
                   name='register'),
               url(r'^logout/$',
                   views.LogoutView.as_view(),
                   name='logout'),
               path(r'account/result.html',
                    views.account_result,
                    name='result')]
