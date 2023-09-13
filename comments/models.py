from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from blog.models import Article


# Create your models here.

class Comment(models.Model):
    body = models.TextField('正文', max_length=300)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('author'),
        on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        verbose_name=_('article'),
        on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self',
        verbose_name=_('parent comment'),
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    is_enable = models.BooleanField(_('enable'),
                                    default=False, blank=False, null=False)

    class Meta:
        ordering = ['-id']
        verbose_name = _('comment')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return self.body
