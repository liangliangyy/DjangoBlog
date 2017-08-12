#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: blog_signals.py
@time: 2017/8/12 上午10:18
"""

import django.dispatch
from django.dispatch import receiver
from django.conf import settings
from DjangoBlog.utils import cache, send_email, expire_view_cache, logger
from DjangoBlog.spider_notify import SpiderNotify
from django.contrib.sites.models import Site

comment_save_signal = django.dispatch.Signal(providing_args=["comment_id", "username", "serverport"])
article_save_signal = django.dispatch.Signal(providing_args=['id', 'is_update_views'])
user_login_logout_signal = django.dispatch.Signal(providing_args=['id', 'type'])


@receiver(article_save_signal)
def article_save_callback(sender, **kwargs):
    id = kwargs['id']
    is_update_views = kwargs['is_update_views']
    type = sender.__name__
    obj = None
    from blog.models import Article, Category, Tag
    if type == 'Article':
        obj = Article.objects.get(id=id)
    elif type == 'Category':
        obj = Category.objects.get(id=id)
    elif type == 'Tag':
        obj = Tag.objects.get(id=id)
    if obj is not None:
        if not settings.TESTING and not is_update_views:
            try:
                notify_url = obj.get_full_url()
                SpiderNotify.baidu_notify([notify_url])
            except Exception as ex:
                logger.error("notify sipder", ex)
                print(ex)


@receiver(comment_save_signal)
def comment_save_callback(sender, **kwargs):
    from comments.models import Comment

    serverport = kwargs['serverport']
    username = kwargs['username']
    comment = Comment.objects.get(id=kwargs['comment_id'])
    site = Site.objects.get_current().domain
    article = comment.article
    # if not settings.DEBUG:
    if True:
        subject = '感谢您发表的评论'
        article_url = "https://{site}{path}".format(site=site, path=comment.article.get_absolute_url())
        html_content = """
        <p>非常感谢您在本站发表评论</p>
        您可以访问
        <a href="%s" rel="bookmark">%s</a>
        来查看您的评论，
        再次感谢您！
        <br />
        如果上面链接无法打开，请将此链接复制至浏览器。
        %s
        """ % (article_url, comment.article.title, article_url)
        tomail = comment.author.email
        send_email([tomail], subject, html_content)

        if comment.parent_comment:
            html_content = """
            您在 <a href="%s" rel="bookmark">%s</a> 的评论 <br/> %s <br/> 收到回复啦.快去看看吧
            <br/>
            如果上面链接无法打开，请将此链接复制至浏览器。
            %s
            """ % (article_url, article.title, comment.parent_comment.body, article_url)
            tomail = comment.parent_comment.author.email
            send_email([tomail], subject, html_content)

    path = article.get_absolute_url()
    site = Site.objects.get_current().domain
    if site.find(':') > 0:
        site = site[0:site.find(':')]

    expire_view_cache(path, servername=site, serverport=serverport, key_prefix='blogdetail')
    if cache.get('seo_processor'):
        cache.delete('seo_processor')
    comment_cache_key = 'article_comments_{id}'.format(id=article.id)
    cache.delete(comment_cache_key)
    from django.core.cache.utils import make_template_fragment_key

    key = make_template_fragment_key('sidebar', [username])
    cache.delete(key)
