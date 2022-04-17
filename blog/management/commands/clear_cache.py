from django.core.management.base import BaseCommand

from djangoblog.utils import cache


class Command(BaseCommand):
    help = 'clear the whole cache'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cleared cache\n'))
