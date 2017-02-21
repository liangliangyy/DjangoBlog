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
from comments.models import Comment
from DjangoBlog.utils import logger, cache


def seo_processor(requests):
    key = 'seo_processor'
    value = cache.get(key)
    if value:
        logger.info('get processor cache.')
        return value
    else:
        logger.info('set processor cache.')
        value = {
            'SITE_NAME': settings.SITE_NAME,
            'SHOW_GOOGLE_ADSENSE': settings.SHOW_GOOGLE_ADSENSE,
            'SITE_SEO_DESCRIPTION': settings.SITE_SEO_DESCRIPTION,
            'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
            'SITE_KEYWORDS': settings.SITE_SEO_KEYWORDS,
            'SITE_BASE_URL': requests.scheme + '://' + requests.get_host() + '/',
            'ARTICLE_SUB_LENGTH': settings.ARTICLE_SUB_LENGTH,
            'nav_category_list': Category.objects.all(),
            'nav_pages': Article.objects.filter(type='p', status='p'),
            # 'MAX_COMMENTID': Comment.objects.latest().pk,
            # 'MAX_ARTICLEID': Article.objects.latest().pk
        }
        cache.set(key, value, 60 * 60 * 10)
        return value
