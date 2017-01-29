#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: spider_notify.py
@time: 2017/1/15 下午1:41
"""

from django.contrib.sitemaps import ping_google
import requests
from django.conf import settings


class spider_notify():
    @staticmethod
    def baidu_notify(urls):
        try:
            data = '\n'.join(urls)
            result = requests.post(settings.BAIDU_NOTIFY_URL, data=data)
            print(result.text)
        except Exception as e:
            print(e)

    @staticmethod
    def __google_notify():
        try:
            ping_google('/sitemap.xml')
        except Exception as e:
            print(e)

    @staticmethod
    def notify(self, url):

        spider_notify.baidu_notify(url)
        spider_notify.__google_notify()
