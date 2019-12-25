#!/usr/bin/env python

from django.core.management.base import BaseCommand
from blog.models import Article, Tag, Category


# TODO 参数化
class Command(BaseCommand):
    help = 'Задать индекс поиска'

    def handle(self, *args, **options):
        datas = set([t.name for t in Tag.objects.all()] + [t.name for t in Category.objects.all()])
        print('\n'.join(datas))
