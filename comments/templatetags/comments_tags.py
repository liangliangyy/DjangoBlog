#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: comments_tags.py
@time: 2016/11/2 下午9:17
"""

from django import template
from django.template.loader import render_to_string
from ..models import Comment
from blog.models import Article
from comments.forms import CommentForm

register = template.Library()


@register.simple_tag
def parse_commenttree(commentlist, comment):
    """获得当前评论子评论的列表
        用法: {% parse_commenttree article_comments comment as childcomments %}
    """
    datas = []

    def parse(c):
        childs = commentlist.filter(parent_comment=c, is_enable=True)
        for child in childs:
            datas.append(child)
            parse(child)

    parse(comment)
    return datas


@register.inclusion_tag('comments/tags/comment_item.html')
def show_comment_item(comment, ischild):
    """评论"""
    depth = 1 if ischild else 2
    return {
        'comment_item': comment,
        'depth': depth
    }
