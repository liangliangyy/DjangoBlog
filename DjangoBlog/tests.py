#!/usr/bin/env python

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

        [url](https://www.mtuktarov.com/)


        ''')
        self.assertIsNotNone(c)
        d = {
            'd': 'key1',
            'd2': 'key2'
        }
        data = parse_dict_to_url(d)
        self.assertIsNotNone(data)
