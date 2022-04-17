import os
import re

import jsonpickle
from werobot import WeRoBot
from werobot.replies import ArticlesReply, Article
from django.conf import settings
from djangoblog.utils import get_sha256
from servermanager.api.blogapi import BlogApi
from servermanager.api.commonapi import TuLing
from servermanager.models import commands
from .MemcacheStorage import MemcacheStorage

robot = WeRoBot(token=os.environ.get('DJANGO_WEROBOT_TOKEN')
                      or 'lylinux', enable_session=True)
memstorage = MemcacheStorage()
if memstorage.is_available:
    robot.config['SESSION_STORAGE'] = memstorage
else:
    from werobot.session.filestorage import FileStorage
    import os
    from django.conf import settings

    if os.path.exists(os.path.join(settings.BASE_DIR, 'werobot_session')):
        os.remove(os.path.join(settings.BASE_DIR, 'werobot_session'))
    robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')
blogapi = BlogApi()
tuling = TuLing()


def convert_to_articlereply(articles, message):
    reply = ArticlesReply(message=message)
    from blog.templatetags.blog_tags import truncatechars_content
    for post in articles:
        imgs = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', post.body)
        imgurl = ''
        if imgs:
            imgurl = imgs[0]
        article = Article(
            title=post.title,
            description=truncatechars_content(post.body),
            img=imgurl,
            url=post.get_full_url()
        )
        reply.add_article(article)
    return reply


@robot.filter(re.compile(r"^\?.*"))
def search(message, session):
    s = message.content
    searchstr = str(s).replace('?', '')
    result = blogapi.search_articles(searchstr)
    if result:
        articles = list(map(lambda x: x.object, result))
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return '没有找到相关文章。'


@robot.filter(re.compile(r'^category\s*$', re.I))
def category(message, session):
    categorys = blogapi.get_category_lists()
    content = ','.join(map(lambda x: x.name, categorys))
    return '所有文章分类目录：' + content


@robot.filter(re.compile(r'^recent\s*$', re.I))
def recents(message, session):
    articles = blogapi.get_recent_articles()
    if articles:
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return "暂时还没有文章"


@robot.filter(re.compile('^help$', re.I))
def help(message, session):
    return '''欢迎关注!
            默认会与图灵机器人聊天~~
        你可以通过下面这些命令来获得信息
        ?关键字搜索文章.
        如?python.
        category获得文章分类目录及文章数.
        category-***获得该分类目录文章
        如category-python
        recent获得最新文章
        help获得帮助.
        weather:获得天气
        如weather:西安
        idcard:获得身份证信息
        如idcard:61048119xxxxxxxxxx
        music:音乐搜索
        如music:阴天快乐
        PS:以上标点符号都不支持中文标点~~
        '''


@robot.filter(re.compile(r'^weather\:.*$', re.I))
def weather(message, session):
    return "建设中..."


@robot.filter(re.compile(r'^idcard\:.*$', re.I))
def idcard(message, session):
    return "建设中..."


@robot.handler
def echo(message, session):
    handler = MessageHandler(message, session)
    return handler.handler()


class CommandHandler():
    def __init__(self):
        self.commands = commands.objects.all()

    def run(self, title):
        cmd = list(
            filter(
                lambda x: x.title.upper() == title.upper(),
                self.commands))
        if cmd:
            return self.__run_command__(cmd[0].command)
        else:
            return "未找到相关命令，请输入hepme获得帮助。"

    def __run_command__(self, cmd):
        try:
            str = os.popen(cmd).read()
            return str
        except BaseException:
            return '命令执行出错!'

    def get_help(self):
        rsp = ''
        for cmd in self.commands:
            rsp += '{c}:{d}\n'.format(c=cmd.title, d=cmd.describe)
        return rsp


cmdhandler = CommandHandler()


class MessageHandler():
    def __init__(self, message, session):
        userid = message.source
        self.message = message
        self.session = session
        self.userid = userid
        try:
            info = session[userid]
            self.userinfo = jsonpickle.decode(info)
        except BaseException:
            userinfo = WxUserInfo()
            self.userinfo = userinfo

    @property
    def is_admin(self):
        return self.userinfo.isAdmin

    @property
    def is_password_set(self):
        return self.userinfo.isPasswordSet

    def savesession(self):
        info = jsonpickle.encode(self.userinfo)
        self.session[self.userid] = info

    def handler(self):
        info = self.message.content

        if self.userinfo.isAdmin and info.upper() == 'EXIT':
            self.userinfo = WxUserInfo()
            self.savesession()
            return "退出成功"
        if info.upper() == 'ADMIN':
            self.userinfo.isAdmin = True
            self.savesession()
            return "输入管理员密码"
        if self.userinfo.isAdmin and not self.userinfo.isPasswordSet:
            passwd = settings.WXADMIN
            if settings.TESTING:
                passwd = '123'
            if passwd.upper() == get_sha256(get_sha256(info)).upper():
                self.userinfo.isPasswordSet = True
                self.savesession()
                return "验证通过,请输入命令或者要执行的命令代码:输入helpme获得帮助"
            else:
                if self.userinfo.Count >= 3:
                    self.userinfo = WxUserInfo()
                    self.savesession()
                    return "超过验证次数"
                self.userinfo.Count += 1
                self.savesession()
                return "验证失败，请重新输入管理员密码:"
        if self.userinfo.isAdmin and self.userinfo.isPasswordSet:
            if self.userinfo.Command != '' and info.upper() == 'Y':
                return cmdhandler.run(self.userinfo.Command)
            else:
                if info.upper() == 'HELPME':
                    return cmdhandler.get_help()
                self.userinfo.Command = info
                self.savesession()
                return "确认执行: " + info + " 命令?"
        rsp = tuling.getdata(info)
        return rsp


class WxUserInfo():
    def __init__(self):
        self.isAdmin = False
        self.isPasswordSet = False
        self.Count = 0
        self.Command = ''


"""
@robot.handler
def hello(message, session):
    blogapi = BlogApi()
    result = blogapi.search_articles(message.content)
    if result:
        articles = list(map(lambda x: x.object, result))
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return '没有找到相关文章。'
"""
