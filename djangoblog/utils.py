#!/usr/bin/env python
# encoding: utf-8


import logging
import os
import random
import string
import uuid
from hashlib import sha256

import markdown
import requests
from django.contrib.sites.models import Site
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_max_articleid_commentid():
    from blog.models import Article
    from comments.models import Comment
    return (Article.objects.latest().pk, Comment.objects.latest().pk)


def get_sha256(str):
    m = sha256(str.encode('utf-8'))
    return m.hexdigest()


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))

                m = sha256(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                # logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.debug(
                    'cache_decorator set cache:%s key:%s' %
                    (func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return value

        return news

    return wrapper


def expire_view_cache(path, servername, serverport, key_prefix=None):
    '''
    刷新视图缓存
    :param path:url路径
    :param servername:host
    :param serverport:端口
    :param key_prefix:前缀
    :return:是否成功
    '''
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    request = HttpRequest()
    request.META = {'SERVER_NAME': servername, 'SERVER_PORT': serverport}
    request.path = path

    key = get_cache_key(request, key_prefix=key_prefix, cache=cache)
    if key:
        logger.info('expire_view_cache:get key:{path}'.format(path=path))
        if cache.get(key):
            cache.delete(key)
        return True
    return False


@cache_decorator()
def get_current_site():
    site = Site.objects.get_current()
    return site


class CommonMarkdown:
    @staticmethod
    def _convert_markdown(value):
        md = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'tables',
            ]
        )
        body = md.convert(value)
        toc = md.toc
        return body, toc

    @staticmethod
    def get_markdown_with_toc(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body, toc

    @staticmethod
    def get_markdown(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body


def send_email(emailto, title, content):
    from djangoblog.blog_signals import send_email_signal
    send_email_signal.send(
        send_email.__class__,
        emailto=emailto,
        title=title,
        content=content)


def generate_code() -> str:
    """生成随机数验证码"""
    return ''.join(random.sample(string.digits, 6))


def parse_dict_to_url(dict):
    from urllib.parse import quote
    url = '&'.join(['{}={}'.format(quote(k, safe='/'), quote(v, safe='/'))
                    for k, v in dict.items()])
    return url


def get_blog_setting():
    value = cache.get('get_blog_setting')
    if value:
        return value
    else:
        from blog.models import BlogSettings
        if not BlogSettings.objects.count():
            setting = BlogSettings()
            setting.sitename = 'djangoblog'
            setting.site_description = '基于Django的博客系统'
            setting.site_seo_description = '基于Django的博客系统'
            setting.site_keywords = 'Django,Python'
            setting.article_sub_length = 300
            setting.sidebar_article_count = 10
            setting.sidebar_comment_count = 5
            setting.show_google_adsense = False
            setting.open_site_comment = True
            setting.analyticscode = ''
            setting.beiancode = ''
            setting.show_gongan_code = False
            setting.save()
        value = BlogSettings.objects.first()
        logger.info('set cache get_blog_setting')
        cache.set('get_blog_setting', value)
        return value


def save_user_avatar(url):
    '''
    保存用户头像
    :param url:头像url
    :return: 本地路径
    '''
    setting = get_blog_setting()
    logger.info(url)

    try:
        imgname = url.split('/')[-1]
        if imgname:
            path = r'{basedir}/avatar/{img}'.format(
                basedir=setting.resource_path, img=imgname)
            if os.path.exists(path):
                os.remove(path)
        rsp = requests.get(url, timeout=2)
        if rsp.status_code == 200:
            basepath = r'{basedir}/avatar/'.format(
                basedir=setting.resource_path)
            if not os.path.exists(basepath):
                os.makedirs(basepath)

            imgextensions = ['.jpg', '.png', 'jpeg', '.gif']
            isimage = len([i for i in imgextensions if url.endswith(i)]) > 0
            ext = os.path.splitext(url)[1] if isimage else '.jpg'
            savefilename = str(uuid.uuid4().hex) + ext
            logger.info('保存用户头像:' + basepath + savefilename)
            with open(basepath + savefilename, 'wb+') as file:
                file.write(rsp.content)
            return 'https://resource.lylinux.net/avatar/' + savefilename
    except Exception as e:
        logger.error(e)
        return url


def delete_sidebar_cache():
    from blog.models import LinkShowType
    keys = ["sidebar" + x for x in LinkShowType.values]
    for k in keys:
        logger.info('delete sidebar key:' + k)
        cache.delete(k)


def delete_view_cache(prefix, keys):
    from django.core.cache.utils import make_template_fragment_key
    key = make_template_fragment_key(prefix, keys)
    cache.delete(key)
