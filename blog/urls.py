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
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView


def key_prefixer(request):
    # if it's not there, don't cache
    # return request.GET.get('number')
    return "123"


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^page/(?P<page>\d+)$', views.IndexView.as_view(), name='index_page'),

    url(r'^article/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<article_id>\d+)-(?P<slug>\S+).html$',
        # cache_page(60 * 60 * 10, key_prefix="blogdetail")(views.ArticleDetailView.as_view()),
        views.ArticleDetailView.as_view(),
        name='detail'),

    url(r'^blogpage/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<page_id>\d+)-(?P<slug>[\w-]+).html$',
        views.ArticleDetailView.as_view(),
        name='pagedetail'),

    url(r'^category/(?P<category_name>[\w-]+).html$', views.CategoryDetailView.as_view(), name='category_detail'),
    url(r'^category/(?P<category_name>[\w-]+)/(?P<page>\d+).html$', views.CategoryDetailView.as_view(),
        name='category_detail_page'),
    # url(r'^category/(?P<category_name>[\w-]+)/(?P<page>\d+).html$', views.CategoryDetailView.as_view(),
    #   name='category_detail'),

    url(r'^author/(?P<author_name>\w+).html$', views.AuthorDetailView.as_view(), name='author_detail'),
    url(r'^author/(?P<author_name>\w+)/(?P<page>\d+).html$', views.AuthorDetailView.as_view(),
        name='author_detail_page'),

    url(r'^tag/(?P<tag_name>.+).html$', views.TagDetailView.as_view(), name='tag_detail'),
    url(r'^tag/(?P<tag_name>.+)/(?P<page>\d+).html$', views.TagDetailView.as_view(), name='tag_detail_page'),

    url(r'^upload', views.fileupload, name='upload'),
    url(r'^refresh', views.refresh_memcache, name='refresh')
]
