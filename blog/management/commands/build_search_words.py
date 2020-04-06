#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: build_search_words.py
@time: 2019/9/23 6:58 下午
"""

from django.core.management.base import BaseCommand
from blog.models import Article, Tag, Category


# TODO 参数化
class Command(BaseCommand):
    help = 'build search words'

    def handle(self, *args, **options):
        datas = set([t.name for t in Tag.objects.all()] +
                    [t.name for t in Category.objects.all()])
        print('\n'.join(datas))
