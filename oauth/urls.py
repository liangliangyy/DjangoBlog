#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: urls.py
@time: 2016/11/26 下午5:25
"""

from django.conf.urls import url
from django.views.decorators.cache import cache_page
from . import views

urlpatterns = [
    url(r'^oauth/wbauthorize/(?P<sitename>\w+)$', views.wbauthorize),
    url(r'^oauth/wboauthurl$', views.wboauthurl),
    # url(r'^oauth/wbauthorize/(?P<sitename>\w+)$', views.wbauthorize),
    url(r'^oauth/googleoauthurl', views.googleoauthurl),
    url(r'^oauth/googleauthorize', views.googleauthorize),
]
