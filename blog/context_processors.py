#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: context_processors.py
@time: 2016/11/6 下午4:23
"""
from .models import Category, Article, Tag
from django.conf import settings


def seo_processor(requests):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_BASE_URL': 'http://' + requests.get_host() + '/',
        'ARTICLE_SUB_LENGTH': settings.ARTICLE_SUB_LENGTH,
        'nav_category_list': Category.objects.all()
    }
