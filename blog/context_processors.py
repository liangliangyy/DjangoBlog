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
from .models import Category, Article, Tag, BlogSettings
from django.conf import settings
from comments.models import Comment
from DjangoBlog.utils import logger, cache, get_blog_setting


def seo_processor(requests):
    key = 'seo_processor'
    value = cache.get(key)
    if value:
        logger.info('get processor cache.')
        return value
    else:
        logger.info('set processor cache.')
        setting = get_blog_setting()
        value = {
            'SITE_NAME': setting.sitename,
            'SHOW_GOOGLE_ADSENSE': setting.show_google_adsense,
            'GOOGLE_ADSENSE_CODES': setting.google_adsense_codes,
            'SITE_SEO_DESCRIPTION': setting.site_seo_description,
            'SITE_DESCRIPTION': setting.site_description,
            'SITE_KEYWORDS': setting.site_keywords,
            'SITE_BASE_URL': requests.scheme + '://' + requests.get_host() + '/',
            'ARTICLE_SUB_LENGTH': setting.article_sub_length,
            'nav_category_list': Category.objects.all(),
            'nav_pages': Article.objects.filter(type='p', status='p'),
            'OPEN_SITE_COMMENT': setting.open_site_comment,
            'BEIAN_CODE': setting.beiancode,
            'ANALYTICS_CODE': setting.analyticscode,

        }
        cache.set(key, value, 60 * 60 * 10)
        return value
