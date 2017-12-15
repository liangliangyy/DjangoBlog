from django.db import models

# Create your models here.
from django.conf import settings
from django.utils.timezone import now


class OAuthUser(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', blank=True, null=True)
    openid = models.CharField(max_length=50)
    nikename = models.CharField(max_length=50, verbose_name='昵称')
    token = models.CharField(max_length=150, null=True, blank=True)
    picture = models.CharField(max_length=350, blank=True, null=True)
    type = models.CharField(blank=False, null=False, max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    matedata = models.CharField(max_length=2000, null=True, blank=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.nikename

    class Meta:
        verbose_name = 'oauth用户'
        verbose_name_plural = verbose_name
