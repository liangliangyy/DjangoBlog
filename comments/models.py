from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from  blog.models import Article
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
import _thread
from DjangoBlog.utils import cache


# Create your models here.

class Comment(models.Model):
    # url = models.URLField('地址', blank=True, null=True)
    # email = models.EmailField('电子邮件', blank=True, null=True)

    body = models.TextField('正文', max_length=300)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', verbose_name="上级评论", blank=True, null=True)

    class Meta:
        ordering = ['created_time']
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'

    def send_comment_email(self, msg):
        try:
            msg.send()
        except:
            pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        subject = '感谢您发表的评论'
        site = Site.objects.get_current().domain
        article_url = "https://{site}{path}".format(site=site, path=self.article.get_absolute_url())
        html_content = """
        <p>非常感谢您在本站发表评论</p>
        您可以访问
        <a href="%s" rel="bookmark">%s</a>
        来查看您的评论，
        再次感谢您！
        <br />
        如果上面链接无法打开，请将此链接复制至浏览器。
        %s
        """ % (article_url, self.article.title, article_url)
        tomail = self.author.email
        msg = EmailMultiAlternatives(subject, html_content, from_email='no-reply@lylinux.net', to=[tomail])

        msg.content_subtype = "html"

        _thread.start_new_thread(self.send_comment_email, (msg,))

        if self.parent_comment:
            html_content = """
            您在 <a href="%s" rel="bookmark">%s</a> 的评论 <br/> %s <br/> 收到回复啦.快去看看吧
            <br/>
            如果上面链接无法打开，请将此链接复制至浏览器。
            %s
            """ % (article_url, self.article.title, self.parent_comment.body, article_url)
            tomail = self.parent_comment.author.email
            msg = EmailMultiAlternatives(subject, html_content, from_email='no-reply@lylinux.net', to=[tomail])
            msg.content_subtype = "html"

            _thread.start_new_thread(self.send_comment_email, (msg,))

        def __str__(self):
            return self.body
