from django.db import models


# Create your models here.
class commands(models.Model):
    title = models.CharField('Название', max_length=300)
    command = models.CharField('Команда', max_length=2000)
    describe = models.CharField('Описание', max_length=300)
    created_time = models.DateTimeField('Время создания', auto_now_add=True)
    last_mod_time = models.DateTimeField('Время изменения', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = verbose_name


class EmailSendLog(models.Model):
    emailto = models.CharField('Адресат', max_length=300)
    title = models.CharField('Заголовок сообщения', max_length=2000)
    content = models.TextField('Содержимое')
    send_result = models.BooleanField('Результат отправки', default=False)
    created_time = models.DateTimeField('Время создания', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Почтовый журнал'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
