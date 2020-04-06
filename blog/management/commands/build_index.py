#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: build_index.py
@time: 2019-04-20 20:39
"""

from blog.documents import ElapsedTimeDocument, ArticleDocumentManager

from django.core.management.base import BaseCommand
from blog.models import Article


# TODO 参数化
class Command(BaseCommand):
    help = 'build search index'

    def handle(self, *args, **options):
        manager = ArticleDocumentManager()
        manager.delete_index()
        manager.rebuild()

        manager = ElapsedTimeDocument()
        manager.init()
