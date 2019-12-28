from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.urls import reverse
from DjangoBlog.utils import get_current_site
from django.utils.timezone import now


# Create your models here.

class BlogUser(AbstractUser):
    nickname = models.CharField('Блогнэйм', max_length=100, blank=True)
    created_time = models.DateTimeField('Время создания', default=now)
    last_mod_time = models.DateTimeField('Время изменения', default=now)
    source = models.CharField("Source", max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse('blog:author_detail', kwargs={'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ['-id']
        verbose_name = "Пользователь"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
