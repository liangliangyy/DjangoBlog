#!/usr/bin/env python

from django import template
from django.template.loader import render_to_string
from ..models import Comment
from blog.models import Article
from comments.forms import CommentForm

register = template.Library()


@register.simple_tag
def parse_commenttree(commentlist, comment):
    """Get a list of current comment sub-comments
        Usage: {% parse_commenttree article_comments comment as childcomments %}
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
    """Comment"""
    depth = 1 if ischild else 2
    return {
        'comment_item': comment,
        'depth': depth
    }
