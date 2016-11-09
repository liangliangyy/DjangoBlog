#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: blog_tags.py
@time: 2016/11/2 下午11:10
"""

from django import template
from django.conf import settings
import markdown2
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import random
from blog.models import Article, Category, Tag
from django.utils.encoding import force_text

register = template.Library()


@register.simple_tag
def timeformat(data):
    try:
        return data.strftime(settings.TIME_FORMAT)
        # print(data.strftime(settings.TIME_FORMAT))
        # return "ddd"
    except:
        return ""


@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except:
        return ""


@register.filter(is_safe=True)
@stringfilter
def custom_markdown(content):
    return mark_safe(markdown2.markdown(force_text(content),
                                        extras=["fenced-code-blocks", "cuddled-lists", "metadata", "tables",
                                                "spoiler"]))
    """
    return mark_safe(markdown.markdown(content,
                                       extensions=
                                       ['markdown.extensions.fenced_code',
                                        'markdown.extensions.codehilite'],
                                       safe_mode=True, enable_attributes=False))
    """

@register.inclusion_tag('blog/breadcrumb.html')
def parsecategoryname(article):
    names = article.get_category_tree()

    names.append((settings.SITE_NAME, 'http://127.0.0.1:8000'))
    names = names[::-1]
    print(names)
    return {'names': names}


@register.inclusion_tag('blog/articletaglist.html')
def loadarticletags(article):
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


@register.inclusion_tag('blog/sidebar.html')
def loadsidebartags():
    recent_articles = Article.objects.filter(status='p')[:settings.SIDEBAR_ARTICLE_COUNT]
    sidebar_categorys = Category.objects.all()
    most_read_articles = Article.objects.filter(status='p').order_by('-views')[:settings.SIDEBAR_ARTICLE_COUNT]
    dates = Article.objects.datetimes('created_time', 'month', order='DESC')
    print(dates)
    # tags=
    return {
        'recent_articles': recent_articles,
        'sidebar_categorys': sidebar_categorys,
        'most_read_articles': most_read_articles,
        'article_dates': dates
    }


"""
@register.tag
def parseCategoryName(parser,token):
    tag_name, category = token.split_contents()
    print(category)
    print(tag_name)
    return CategoryNametag(category)

class CategoryNametag(template.Node):
    def __init__(self,category):
        self.category=category
        self.names=[]


    def parseCategory(self,category):
        self.names.append(category.name)
        if category.parent_category:
            self.parseCategory(category.parent_category)


    def render(self, context):
        self.parseCategory(self.category)
        print(self.names)
        return " > ".join(self.names)

        #if self.category.parent_category:
"""
