#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: utils.py
@time: 2017/1/19 上午2:30
"""
from django.core.cache import cache
from hashlib import md5
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
import logging

logger = logging.getLogger('djangoblog')
from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def get_max_articleid_commentid():
    from blog.models import Article
    from comments.models import Comment
    return (Article.objects.latest().pk, Comment.objects.latest().pk)


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            key = ''
            try:
                view = args[0]
                key = view.get_cache_key()
            except:
                key = None
                pass
            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value:
                logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                return value
            else:
                logger.info('cache_decorator set cache:%s key:%s' % (func.__name__, key))
                value = func(*args, **kwargs)
                cache.set(key, value, expiration)
                return value

        return news

    return wrapper


def expire_view_cache(path, servername, serverport, key_prefix=None):
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
    except:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class BlogMarkDownRenderer(mistune.Renderer):
    def block_code(self, text, lang):
        # renderer has an options
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)


class common_markdown():
    @staticmethod
    def get_markdown(value):
        renderer = BlogMarkDownRenderer(inlinestyles=False)

        mdp = mistune.Markdown(escape=True, renderer=renderer)
        return mdp(value)
