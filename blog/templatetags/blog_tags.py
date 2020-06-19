#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: blog_tags.py
@time: 2016/11/2 下午11:10
"""

from django import template
from django.db.models import Q
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import random
from django.urls import reverse
from blog.models import Article, Category, Tag, Links, SideBar, LinkShowType
from django.utils.encoding import force_text
from django.shortcuts import get_object_or_404
import hashlib
import urllib
from comments.models import Comment
from DjangoBlog.utils import cache_decorator, cache
from django.contrib.auth import get_user_model
from oauth.models import OAuthUser
from DjangoBlog.utils import get_current_site
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag
def timeformat(data):
    try:
        return data.strftime(settings.TIME_FORMAT)
        # print(data.strftime(settings.TIME_FORMAT))
        # return "ddd"
    except Exception as e:
        logger.error(e)
        return ""


@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.filter(is_safe=True)
@stringfilter
def custom_markdown(content):
    from DjangoBlog.utils import CommonMarkdown
    return mark_safe(CommonMarkdown.get_markdown(content))


@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    获得文章内容的摘要
    :param content:
    :return:
    """
    from django.template.defaultfilters import truncatechars_html
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    return truncatechars_html(content, blogsetting.article_sub_length)


@register.filter(is_safe=True)
@stringfilter
def truncate(content):
    from django.utils.html import strip_tags

    return strip_tags(content)[:150]


@register.inclusion_tag('blog/tags/breadcrumb.html')
def load_breadcrumb(article):
    """
    获得文章面包屑
    :param article:
    :return:
    """
    names = article.get_category_tree()
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    site = get_current_site().domain
    names.append((blogsetting.sitename, '/'))
    names = names[::-1]

    return {
        'names': names,
        'title': article.title
    }


@register.inclusion_tag('blog/tags/article_tag_list.html')
def load_articletags(article):
    """
    文章标签
    :param article:
    :return:
    """
    tags = article.tags.all()
    tags_list = []
    for tag in tags:
        url = tag.get_absolute_url()
        count = tag.get_article_count()
        tags_list.append((
            url, count, tag, random.choice(settings.BOOTSTRAP_COLOR_TYPES)
        ))
    return {
        'article_tags_list': tags_list
    }


@register.inclusion_tag('blog/tags/sidebar.html')
def load_sidebar(user, linktype):
    """
    加载侧边栏
    :return:
    """
    logger.info('load sidebar')
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    recent_articles = Article.objects.filter(
        status='p')[:blogsetting.sidebar_article_count]
    sidebar_categorys = Category.objects.all()
    extra_sidebars = SideBar.objects.filter(
        is_enable=True).order_by('sequence')
    most_read_articles = Article.objects.filter(status='p').order_by(
        '-views')[:blogsetting.sidebar_article_count]
    dates = Article.objects.datetimes('created_time', 'month', order='DESC')
    links = Links.objects.filter(is_enable=True).filter(
        Q(show_type=str(linktype)) | Q(show_type=LinkShowType.A))
    commment_list = Comment.objects.filter(is_enable=True).order_by(
        '-id')[:blogsetting.sidebar_comment_count]
    # 标签云 计算字体大小
    # 根据总数计算出平均值 大小为 (数目/平均值)*步长
    increment = 5
    tags = Tag.objects.all()
    sidebar_tags = None
    if tags and len(tags) > 0:
        s = [t for t in [(t, t.get_article_count()) for t in tags] if t[1]]
        count = sum([t[1] for t in s])
        dd = 1 if (count == 0 or not len(tags)) else count / len(tags)
        import random
        sidebar_tags = list(
            map(lambda x: (x[0], x[1], (x[1] / dd) * increment + 10), s))
        random.shuffle(sidebar_tags)

    return {
        'recent_articles': recent_articles,
        'sidebar_categorys': sidebar_categorys,
        'most_read_articles': most_read_articles,
        'article_dates': dates,
        'sidebar_comments': commment_list,
        'user': user,
        'sidabar_links': links,
        'show_google_adsense': blogsetting.show_google_adsense,
        'google_adsense_codes': blogsetting.google_adsense_codes,
        'open_site_comment': blogsetting.open_site_comment,
        'show_gongan_code': blogsetting.show_gongan_code,
        'sidebar_tags': sidebar_tags,
        'extra_sidebars': extra_sidebars
    }


@register.inclusion_tag('blog/tags/article_meta_info.html')
def load_article_metas(article, user):
    """
    获得文章meta信息
    :param article:
    :return:
    """
    return {
        'article': article,
        'user': user
    }


@register.inclusion_tag('blog/tags/article_pagination.html')
def load_pagination_info(page_obj, page_type, tag_name):
    previous_url = ''
    next_url = ''
    if page_type == '':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse('blog:index_page', kwargs={'page': next_number})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:index_page', kwargs={
                    'page': previous_number})
    if page_type == '分类标签归档':
        tag = get_object_or_404(Tag, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': next_number,
                    'tag_name': tag.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': previous_number,
                    'tag_name': tag.slug})
    if page_type == '作者文章归档':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': next_number,
                    'author_name': tag_name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': previous_number,
                    'author_name': tag_name})

    if page_type == '分类目录归档':
        category = get_object_or_404(Category, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': next_number,
                    'category_name': category.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': previous_number,
                    'category_name': category.slug})

    return {
        'previous_url': previous_url,
        'next_url': next_url,
        'page_obj': page_obj
    }


"""
@register.inclusion_tag('nav.html')
def load_nav_info():
    category_list = Category.objects.all()
    return {
        'nav_category_list': category_list
    }
"""


@register.inclusion_tag('blog/tags/article_info.html')
def load_article_detail(article, isindex, user):
    """
    加载文章详情
    :param article:
    :param isindex:是否列表页，若是列表页只显示摘要
    :return:
    """
    from DjangoBlog.utils import get_blog_setting
    blogsetting = get_blog_setting()

    return {
        'article': article,
        'isindex': isindex,
        'user': user,
        'open_site_comment': blogsetting.open_site_comment,
    }


# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    """获得gravatar头像"""
    cachekey = 'gravatat/' + email
    if cache.get(cachekey):
        return cache.get(cachekey)
    else:
        usermodels = OAuthUser.objects.filter(email=email)
        if usermodels:
            o = list(filter(lambda x: x.picture is not None, usermodels))
            if o:
                return o[0].picture
        email = email.encode('utf-8')

        default = "https://resource.lylinux.net/image/2017/03/26/120117.jpg".encode(
            'utf-8')

        url = "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(
            email.lower()).hexdigest(), urllib.parse.urlencode({'d': default, 's': str(size)}))
        cache.set(cachekey, url, 60 * 60 * 10)
        return url


@register.filter
def gravatar(email, size=40):
    """获得gravatar头像"""
    url = gravatar_url(email, size)
    return mark_safe(
        '<img src="%s" height="%d" width="%d">' %
        (url, size, size))


@register.simple_tag
def query(qs, **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)
