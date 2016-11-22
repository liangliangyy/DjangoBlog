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
@time: 2016/11/2 下午7:15
"""

from django.conf.urls import url
from django.views.decorators.cache import cache_page
from . import views

urlpatterns = [
    # url(r'^$', cache_page(60 * 15)(views.IndexView.as_view()), name='index'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^article/(?P<article_id>\d+)$', views.ArticleDetailView.as_view(), name='detail'),

    url(r'(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<article_id>\d+)-(?P<slug>\S+).html$',
        views.ArticleDetailView.as_view(),
        name='detail'),
    url(r'^category/(?P<category_name>\w+)$', views.CategoryDetailView.as_view(), name='category_detail'),
    url(r'^author/(?P<author_name>\w+)$', views.AuthorDetailView.as_view(), name='author_detail'),
    url(r'^tags/(?P<tag_name>\w+)$', views.TagDetailView.as_view(), name='tag_detail'),
]
