from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


class Article(models.Model):
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )

    title = models.CharField('标题', max_length=200)
    body = models.TextField('正文')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    pub_time = models.DateTimeField('发布时间', blank=True, null=True,
                                    help_text="不指定发布时间则视为草稿，可以指定未来时间，到时将自动发布。")
    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES)
    summary = models.CharField('摘要', max_length=200, blank=True, help_text="可选，若为空将摘取正文的前54个字符。")
    views = models.PositiveIntegerField('浏览量', default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE)

    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'article_id': self.pk})

    def save(self, *args, **kwargs):
        self.summary = self.summary or self.body[:120]
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])


class Category(models.Model):
    name = models.CharField('分类名', max_length=30)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('标签名', max_length=30)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name
