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
import datetime

register = template.Library()


@register.simple_tag
def timeformat(data):
    try:

        print(data.strftime(settings.TIME_FORMAT))
        return "ddd"
    except:
        return "111"
