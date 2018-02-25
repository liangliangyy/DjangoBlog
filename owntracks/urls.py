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
@time: 2018/2/25 下午3:04
"""
from django.urls import path
from . import views

app_name = "owntracks"

urlpatterns = [
    path('owntracks/logtracks', views.manage_owntrack_log),
    path('owntracks/show_maps', views.show_maps),
    path('owntracks/get_datas', views.get_datas)
]

# http://home.lylinux.net:2213/owntracks/logtracks
