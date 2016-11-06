from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse


# Create your models here.
class BlogUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=50, blank=True)
    mugshot = models.ImageField('头像', upload_to='upload/mugshots', blank=True)

    def get_absolute_url(self):
        return reverse('blog:author_detail', kwargs={'author_name': self.username})
