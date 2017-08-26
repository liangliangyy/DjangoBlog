from django.db import models


# Create your models here.
class commands(models.Model):
    title = models.CharField('命令标题', max_length=300)
    command = models.CharField('命令', max_length=2000)
    describe = models.CharField('命令描述', max_length=300)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
