# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class OAuthUser(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('author'),
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, verbose_name=_('nick name'))
    token = models.CharField(max_length=150, null=True, blank=True)
    picture = models.CharField(max_length=350, blank=True, null=True)
    type = models.CharField(blank=False, null=False, max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = _('oauth user')
        verbose_name_plural = verbose_name
        ordering = ['-creation_time']


class OAuthConfig(models.Model):
    TYPE = (
        ('weibo', _('weibo')),
        ('google', _('google')),
        ('github', 'GitHub'),
        ('facebook', 'FaceBook'),
        ('qq', 'QQ'),
    )
    type = models.CharField(_('type'), max_length=10, choices=TYPE, default='a')
    appkey = models.CharField(max_length=200, verbose_name='AppKey')
    appsecret = models.CharField(max_length=200, verbose_name='AppSecret')
    callback_url = models.CharField(
        max_length=200,
        verbose_name=_('callback url'),
        blank=False,
        default='')
    is_enable = models.BooleanField(
        _('is enable'), default=True, blank=False, null=False)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)

    def clean(self):
        if OAuthConfig.objects.filter(
                type=self.type).exclude(id=self.id).count():
            raise ValidationError(_(self.type + _('already exists')))

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'oauth配置'
        verbose_name_plural = verbose_name
        ordering = ['-creation_time']
