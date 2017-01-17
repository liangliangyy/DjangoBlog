#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: ping_baidu.py
@time: 2017/1/17 下午15:29
"""

from django.core.management.base import BaseCommand, CommandError
from blog.models import Article
from DjangoBlog.spider_notify import sipder_notify


class Command(BaseCommand):
    help = 'notify baidu url'

    def handle(self, *args, **options):
        notify = sipder_notify()
        for article in Article.objects.filter(status='p'):
            try:
                url = article.get_full_url()
                notify.baidu_notify(url=url)
                self.stdout.write(self.style.SUCCESS('Successfully notify article id : "%s"' % article.pk))
            except Exception as e:
                self.stdout.write('error:' + str(e))
        self.stdout.write(self.style.SUCCESS('finish notify'))
