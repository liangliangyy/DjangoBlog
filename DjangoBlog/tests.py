#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: tests.py
@time: 2017/10/25 下午10:16
"""

from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from DjangoBlog.utils import get_current_site
from django.urls import reverse
import datetime
from DjangoBlog.utils import *


class DjangoBlogTest(TestCase):
    def setUp(self):
        pass

    def test_utils(self):
        md5 = get_md5('test')
        self.assertIsNotNone(md5)
        c = CommonMarkdown.get_markdown('''
        # Title1

        ```python
        import os
        ```

        [url](https://www.lylinux.net/)

        [ddd](http://www.baidu.com)


        ''')
        self.assertIsNotNone(c)
        d = {
            'd': 'key1',
            'd2': 'key2'
        }
        data = parse_dict_to_url(d)
        self.assertIsNotNone(data)
        render = BlogMarkDownRenderer()
        s = render.autolink('http://www.baidu.com')
        self.assertTrue(s.find('nofollow') > 0)
        s = render.link('http://www.baidu.com', 'test', 'test')
        self.assertTrue(s.find('nofollow') > 0)
