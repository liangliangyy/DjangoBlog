#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: utils.py
@time: 2017/1/19 上午2:30
"""
from django.core.cache import cache
from django.contrib.sites.models import Site
from hashlib import md5
import mistune
from mistune import escape, escape_link
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
import logging
import requests
import uuid
import os

logger = logging.getLogger(__name__)


def get_max_articleid_commentid():
    from blog.models import Article
    from comments.models import Comment
    return (Article.objects.latest().pk, Comment.objects.latest().pk)


def get_md5(str):
    m = md5(str.encode('utf-8'))
    return m.hexdigest()


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except BaseException:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                # logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.info(
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


def block_code(text, lang, inlinestyles=False, linenos=False):
    '''
    markdown代码高亮
    :param text:
    :param lang:
    :param inlinestyles:
    :param linenos:
    :return:
    '''
    if not lang:
        text = text.strip()
        return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter(
            noclasses=inlinestyles, linenos=linenos
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="highlight">%s</div>\n' % code
        return code
    except BaseException:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


@cache_decorator()
def get_current_site():
    site = Site.objects.get_current()
    return site


class BlogMarkDownRenderer(mistune.Renderer):
    '''
    markdown渲染
    '''

    def block_code(self, text, lang=None):
        # renderer has an options
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)

    def autolink(self, link, is_email=False):
        text = link = escape(link)

        if is_email:
            link = 'mailto:%s' % link
        if not link:
            link = "#"
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        return '<a href="%s" %s>%s</a>' % (link, nofollow, text)

    def link(self, link, title, text):
        link = escape_link(link)
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        if not link:
            link = "#"
        if not title:
            return '<a href="%s" %s>%s</a>' % (link, nofollow, text)
        title = escape(title, quote=True)
        return '<a href="%s" title="%s" %s>%s</a>' % (
            link, title, nofollow, text)


class CommonMarkdown():
    @staticmethod
    def get_markdown(value):
        renderer = BlogMarkDownRenderer(inlinestyles=False)

        mdp = mistune.Markdown(escape=True, renderer=renderer)
        return mdp(value)


def send_email(emailto, title, content):
    from DjangoBlog.blog_signals import send_email_signal
    send_email_signal.send(
        send_email.__class__,
        emailto=emailto,
        title=title,
        content=content)


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
            setting.sitename = 'DjangoBlog'
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
    except BaseException:
        pass
    try:
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


def delete_sidebar_cache(username):
    from django.core.cache.utils import make_template_fragment_key
    from blog.models import LINK_SHOW_TYPE
    keys = (
        make_template_fragment_key(
            'sidebar', [
                username + x[0]]) for x in LINK_SHOW_TYPE)
    for k in keys:
        logger.info('delete sidebar key:' + k)
        cache.delete(k)


def delete_view_cache(prefix, keys):
    from django.core.cache.utils import make_template_fragment_key
    key = make_template_fragment_key(prefix, keys)
    cache.delete(key)
