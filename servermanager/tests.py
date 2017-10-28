from django.test import Client, RequestFactory, TestCase
from django.contrib.sites.models import Site
from .models import commands
import datetime
from accounts.models import BlogUser
from blog.models import Category, Article
from .robot import search, category, recents
from werobot.messages.messages import TextMessage
from .robot import MessageHandler, CommandHandler
from servermanager.Api.commonapi import TuLing


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
        site = Site.objects.get_current().domain
        user = BlogUser.objects.create_superuser(email="liangliangyy1@gmail.com",
                                                 username="liangliangyy1", password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')

        c = Category()
        c.name = "categoryccc"
        c.created_time = datetime.datetime.now()
        c.last_mod_time = datetime.datetime.now()
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
        s.content = "nicetitleccc"
        rsp = search(s, None)
        self.assertTrue(rsp != '没有找到相关文章。')
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
        d = msghandler.is_admin
        e = msghandler.is_password_set
        msghandler.userinfo.isPasswordSet = True
        msghandler.userinfo.isAdmin = True
        msghandler.handler()
        s.content = 'y'
        msghandler.handler()
        s.content='idcard:12321233'
        msghandler.handler()
        s.content='weather:上海'
        msghandler.handler()
        s.content='admin'
        msghandler.handler()
        s.content='123'
        msghandler.handler()