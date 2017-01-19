#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: feed.py
@time: 2016/12/22 下午10:16
"""

from django.contrib.syndication.views import Feed
from blog.models import Article
from django.conf import settings
from django.utils.feedgenerator import Rss201rev2Feed
from DjangoBlog.utils import common_markdown
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class DjangoBlogFeed(Feed):
    feed_type = Rss201rev2Feed

    description = settings.SITE_DESCRIPTION
    feed_url = 'https://www.lylinux.net/feed'
    title = "%s %s " % (settings.SITE_NAME, settings.SITE_DESCRIPTION)
    link = "https://www.lylinux.net"

    def author_name(self):
        return get_user_model().objects.first().nickname

    def author_link(self):
        return get_user_model().objects.first().get_absolute_url()

    def items(self):
        return Article.objects.order_by('-pk')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return common_markdown.get_markdown(item.body)

    def feed_copyright(self):
        # print(Site.objects.get_current().name)
        return "Copyright© 2017  " + settings.SITE_NAME

    def item_link(self, item):
        return item.get_absolute_url()

    def item_guid(self, item):
        return
