#!/usr/bin/env python

from blog.documents import ElapsedTimeDocument, ArticleDocumentManager
from django.core.management.base import BaseCommand
from blog.models import Article


# TODO parameterize
class Command(BaseCommand):
    help = 'Задать индекс поиска'

    def handle(self, *args, **options):
        manager = ArticleDocumentManager()
        manager.delete_index()
        manager.rebuild()

        manager = ElapsedTimeDocument()
        manager.init()
