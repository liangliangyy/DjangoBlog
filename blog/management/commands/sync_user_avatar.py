#!/usr/bin/env python

from django.core.management.base import BaseCommand
from oauth.models import OAuthUser
from DjangoBlog.utils import save_user_avatar


class Command(BaseCommand):
    help = 'sync user avatar'

    def handle(self, *args, **options):
        users = OAuthUser.objects.filter(picture__isnull=False).exclude(
            picture__istartswith='https://resource.mtuktarov.com').all()
        self.stdout.write('Начинаем синхронизацию{count}аватаров'.format(count=len(users)))
        for u in users:
            self.stdout.write('Начать синхронизацию:{id}'.format(id=u.nikename))
            url = u.picture
            url = save_user_avatar(url)
            if url:
                self.stdout.write('Завершить синхронизацию:{id}.url:{url}'.format(id=u.nikename, url=url))
                u.picture = url
                u.save()
        self.stdout.write('Завершить синхронизацию')
