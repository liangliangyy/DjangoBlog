from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.urls import reverse
from DjangoBlog.utils import get_current_site
from django.utils.timezone import now


# Create your models here.

class BlogUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=100, blank=True)
    mugshot = models.ImageField('头像', upload_to='upload/mugshots', blank=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    # objects = BlogUserManager()

    def get_absolute_url(self):
        return reverse('blog:author_detail', kwargs={'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url
