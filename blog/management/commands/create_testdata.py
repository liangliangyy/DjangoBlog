#!/usr/bin/env python

from django.core.management.base import BaseCommand
from blog.models import Article, Tag, Category
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import datetime


class Command(BaseCommand):
    help = 'create test datas'

    def handle(self, *args, **options):
        user = \
            get_user_model().objects.get_or_create(email='test', username='test',
                                                   password='test!q@w#eTYU')[0]

        pcategory = Category.objects.get_or_create(name='pcategory', parent_category=None)[0]

        category = Category.objects.get_or_create(name='category', parent_category=pcategory)[0]

        category.save()
        basetag = Tag()
        basetag.name = "basetag.name"
        basetag.save()
        for i in range(1, 20):
            article = Article.objects.get_or_create(category=category,
                                                    title='nice title ' + str(i),
                                                    body='nice content ' + str(i),
                                                    author=user
                                                    )[0]
            tag = Tag()
            tag.name = "tag.name" + str(i)
            tag.save()
            article.tags.add(tag)
            article.tags.add(basetag)
            article.save()

        from DjangoBlog.utils import cache
        cache.clear()
        self.stdout.write(self.style.SUCCESS('created test datas \n'))
