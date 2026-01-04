#!/usr/bin/env python
# encoding: utf-8


import logging
import os
import random
import string
import uuid
import hashlib
import hmac

import bleach
import markdown
import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.templatetags.static import static

logger = logging.getLogger(__name__)


def get_max_articleid_commentid():
    from blog.models import Article
    from comments.models import Comment
    return (Article.objects.latest().pk, Comment.objects.latest().pk)


def get_sha256(value):
    key = settings.SECRET_KEY.encode('utf-8')
    msg = str(value).encode('utf-8')
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


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

                m = hashlib.sha256(unique_str.encode('utf-8'))
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
            setting.site_name = 'djangoblog'
            setting.site_description = '基于Django的博客系统'
            setting.site_seo_description = '基于Django的博客系统'
            setting.site_keywords = 'Django,Python'
            setting.article_sub_length = 300
            setting.sidebar_article_count = 10
            setting.sidebar_comment_count = 5
            setting.show_google_adsense = False
            setting.open_site_comment = True
            setting.analytics_code = ''
            setting.beian_code = ''
            setting.show_gongan_code = False
            setting.comment_need_review = False
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
    logger.info(url)

    try:
        basedir = os.path.join(settings.STATICFILES, 'avatar')
        rsp = requests.get(url, timeout=2)
        if rsp.status_code == 200:
            if not os.path.exists(basedir):
                os.makedirs(basedir)

            image_extensions = ['.jpg', '.png', 'jpeg', '.gif']
            isimage = len([i for i in image_extensions if url.endswith(i)]) > 0
            ext = os.path.splitext(url)[1] if isimage else '.jpg'
            save_filename = str(uuid.uuid4().hex) + ext
            logger.info('保存用户头像:' + basedir + save_filename)
            with open(os.path.join(basedir, save_filename), 'wb+') as file:
                file.write(rsp.content)
            return static('avatar/' + save_filename)
    except Exception as e:
        logger.error(e)
        return static('blog/img/avatar.png')


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


def get_resource_url():
    if settings.STATIC_URL:
        return settings.STATIC_URL
    else:
        site = get_current_site()
        return 'http://' + site.domain + '/static/'


# 允许的HTML标签白名单 - 支持markdown常用元素
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'ul', 'pre', 'strong',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # 标题
    'p', 'span', 'div', 'br', 'hr',  # 段落和分隔
    'table', 'thead', 'tbody', 'tr', 'th', 'td',  # 表格
    'dl', 'dt', 'dd',  # 定义列表
    'img',  # 图片（需配合ALLOWED_ATTRIBUTES限制src）
    'del', 'ins', 'sub', 'sup',  # 文本修饰
]

# 安全的class值白名单 - 只允许代码高亮相关的class
ALLOWED_CLASSES = [
    'codehilite', 'highlight', 'hll', 'c', 'err', 'k', 'l', 'n', 'o', 'p', 'cm', 'cp', 'c1', 'cs',
    'gd', 'ge', 'gr', 'gh', 'gi', 'go', 'gp', 'gs', 'gu', 'gt', 'kc', 'kd', 'kn', 'kp', 'kr', 'kt',
    'ld', 'm', 'mf', 'mh', 'mi', 'mo', 'na', 'nb', 'nc', 'no', 'nd', 'ni', 'ne', 'nf', 'nl', 'nn',
    'nt', 'nv', 'ow', 'w', 'mb', 'mh', 'mi', 'mo', 'sb', 'sc', 'sd', 'se', 'sh', 'si', 'sx', 's2',
    's1', 'ss', 'bp', 'vc', 'vg', 'vi', 'il'
]

def class_filter(tag, name, value):
    """自定义class属性过滤器"""
    if name == 'class':
        # 只允许预定义的安全class值
        allowed_classes = [cls for cls in value.split() if cls in ALLOWED_CLASSES]
        return ' '.join(allowed_classes) if allowed_classes else False
    return value

# 安全的属性白名单
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],  # rel="nofollow" 用于外部链接
    'abbr': ['title'], 
    'acronym': ['title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],  # 图片属性
    'table': ['border', 'cellpadding', 'cellspacing'],
    'th': ['align', 'valign'],
    'td': ['align', 'valign'],
    'span': class_filter,
    'div': class_filter,
    'pre': class_filter,
    'code': class_filter
}

# 安全的协议白名单 - 防止javascript:等危险协议
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def sanitize_html(html):
    """
    安全的HTML清理函数
    使用bleach库进行白名单过滤，防止XSS攻击
    """
    cleaned = bleach.clean(
        html, 
        tags=ALLOWED_TAGS, 
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,  # 限制允许的协议
        strip=True,  # 移除不允许的标签而不是转义
        strip_comments=True  # 移除HTML注释
    )
    
    # 移除空的 style 属性（bleach 有时会保留 style=""）
    import re
    cleaned = re.sub(r'\s*style\s*=\s*["\'][\s]*["\']', '', cleaned)
    
    return cleaned
