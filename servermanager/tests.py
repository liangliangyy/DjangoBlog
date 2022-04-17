from django.test import Client, RequestFactory, TestCase
from django.utils import timezone
from werobot.messages.messages import TextMessage

from djangoblog.utils import get_current_site
from accounts.models import BlogUser
from blog.models import Category, Article
from servermanager.api.commonapi import TuLing
from .models import commands
from .robot import MessageHandler, CommandHandler
from .robot import search, category, recents


# Create your tests here.
class ServerManagerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_tuling(self):
        t = TuLing()
        content = t.getdata('test')
        self.assertIsNotNone(content)

    def test_validate_comment(self):
        site = get_current_site().domain
        user = BlogUser.objects.create_superuser(
            email="liangliangyy1@gmail.com",
            username="liangliangyy1",
            password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')

        c = Category()
        c.name = "categoryccc"
        c.created_time = timezone.now()
        c.last_mod_time = timezone.now()
        c.save()

        article = Article()
        article.title = "nicetitleccc"
        article.body = "nicecontentccc"
        article.author = user
        article.category = c
        article.type = 'a'
        article.status = 'p'
        article.save()
        s = TextMessage([])
        s.content = "nice"
        rsp = search(s, None)
        rsp = category(None, None)
        self.assertIsNotNone(rsp)
        rsp = recents(None, None)
        self.assertTrue(rsp != '暂时还没有文章')

        cmd = commands()
        cmd.title = "test"
        cmd.command = "ls"
        cmd.describe = "test"
        cmd.save()

        cmdhandler = CommandHandler()
        rsp = cmdhandler.run('test')
        self.assertIsNotNone(rsp)
        s.source = 'u'
        s.content = 'test'
        msghandler = MessageHandler(s, {})

        # msghandler.userinfo.isPasswordSet = True
        # msghandler.userinfo.isAdmin = True
        msghandler.handler()
        s.content = 'y'
        msghandler.handler()
        s.content = 'idcard:12321233'
        msghandler.handler()
        s.content = 'weather:上海'
        msghandler.handler()
        s.content = 'admin'
        msghandler.handler()
        s.content = '123'
        msghandler.handler()

        s.content = 'exit'
        msghandler.handler()
