#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: comments_tags.py
@time: 2016/11/2 下午9:17
"""

from django import template
from django.template.loader import render_to_string
from ..models import Comment
from blog.models import Article

register = template.Library()


@register.simple_tag(name='get_comment_count')
def GetCommentCount(parser, token):
    commentcount = Comment.objects.filter(article__author_id=token).count()
    return "0" if commentcount == 0 else str(commentcount) + " comments"
