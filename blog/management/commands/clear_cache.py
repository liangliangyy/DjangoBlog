#!/usr/bin/env python

from DjangoBlog.utils import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Удалить весь кэш'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Кэш удален\n'))
