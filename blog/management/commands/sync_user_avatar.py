#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: sync_user_avatar.py
@time: 2018/7/18 下午10:21
"""

from django.core.management.base import BaseCommand
from oauth.models import OAuthUser
from DjangoBlog.utils import save_user_avatar


class Command(BaseCommand):
    help = 'sync user avatar'

    def handle(self, *args, **options):
        users = OAuthUser.objects.filter(picture__isnull=False).exclude(
            picture__istartswith='https://resource.lylinux.net').all()
        self.stdout.write('开始同步{count}个用户头像'.format(count=len(users)))
        for u in users:
            self.stdout.write('开始同步:{id}'.format(id=u.nikename))
            url = u.picture
            url = save_user_avatar(url)
            if url:
                self.stdout.write(
                    '结束同步:{id}.url:{url}'.format(
                        id=u.nikename, url=url))
                u.picture = url
                u.save()
        self.stdout.write('结束同步')
