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
    path('owntracks/logtracks', views.manage_owntrack_log, name='logtracks'),
    path('owntracks/show_maps', views.show_maps, name='show_maps'),
    path('owntracks/get_datas', views.get_datas, name='get_datas'),
    path('owntracks/show_dates', views.show_log_dates, name='show_dates')
]
