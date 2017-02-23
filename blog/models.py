from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from uuslug import slugify
from DjangoBlog.spider_notify import spider_notify
from django.contrib.sites.models import Site
from DjangoBlog.utils import cache_decorator, logger
from django.utils.functional import cached_property


class BaseModel(models.Model):
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == 'no-slug' or not self.id:
            # Only set the slug when the object is created.
            slug = self.title if 'title' in self.__dict__ else self.name
            self.slug = slugify(slug)
        super().save(*args, **kwargs)

        if 'update_fields' in kwargs and len(kwargs['update_fields']) == 1 and kwargs['update_fields'][0] == 'views':
            return
        try:
            notify_url = self.get_full_url()
            spider_notify.baidu_notify([notify_url])
        except Exception as ex:
            logger.error("notify sipder", ex)
            print(ex)

    def get_full_url(self):
        site = Site.objects.get_current().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True


class Article(BaseModel):
    """文章"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    TYPE = (
        ('a', '文章'),
        ('p', '页面'),
    )
    title = models.CharField('标题', max_length=200, unique=True)
    body = models.TextField('正文')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    pub_time = models.DateTimeField('发布时间', blank=True, null=True)
    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    type = models.CharField('类型', max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField('浏览量', default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE)

    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'

    def get_absolute_url(self):

        return reverse('blog:detail', kwargs=
        {
            'article_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day,
            'slug': self.slug
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        names = []

        def parse(category):
            names.append((category.name, category.get_absolute_url()))
            if category.parent_category:
                parse(category.parent_category)

        parse(self.category)
        return names

    def save(self, *args, **kwargs):
        # self.summary = self.summary or self.body[:settings.ARTICLE_SUB_LENGTH]
        if not self.slug or self.slug == 'no-slug' or not self.id:
            # Only set the slug when the object is created.
            self.slug = slugify(self.title)
            """
            try:
                notify = sipder_notify()
                notify.notify(self.get_full_url())
            except Exception as e:
                print(e)
            """
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    """
    def comment_list(self):
        comments = self.comment_set.all()
        parent_comments = comments.filter(parent_comment=None)
    """

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cached_property
    def next_article(self):
        # 下一篇
        return Article.objects.filter(id__gt=self.id, status='p').order_by('id').first()

    @cached_property
    def prev_article(self):
        # 前一篇
        return Article.objects.filter(id__lt=self.id, status='p').first()


'''
class BlogPage(models.Model):
    """文章"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    title = models.CharField('标题', max_length=200)
    body = models.TextField('正文')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    pub_time = models.DateTimeField('发布时间', blank=True, null=True,
                                    help_text="不指定发布时间则视为草稿，可以指定未来时间，到时将自动发布。")
    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES, default='o')
    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS)
    # summary = models.CharField('摘要', max_length=200, blank=True, help_text="可选，若为空将摘取正文的前300个字符。")
    views = models.PositiveIntegerField('浏览量', default=0)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    class Meta:
        ordering = ['-pub_time']
        verbose_name = "页面"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:pagedetail', kwargs=
        {
            'page_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day,
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        # self.summary = self.summary or self.body[:settings.ARTICLE_SUB_LENGTH]
        if not self.slug or self.slug == 'no-slug' or not self.id:
            # Only set the slug when the object is created.
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        comments = self.comment_set.all()
        parent_comments = comments.filter(parent_comment=None)

    def get_category_tree(self):
        return []
'''


class Category(BaseModel):
    """文章分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    parent_category = models.ForeignKey('self', verbose_name="父级分类", blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'category_name': self.slug})

    def __str__(self):
        return self.name


class Tag(BaseModel):
    """文章标签"""
    name = models.CharField('标签名', max_length=30, unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class Links(models.Model):
    """友情链接"""
    name = models.CharField('链接名称', max_length=30, unique=True)
    link = models.URLField('链接地址')
    sequence = models.IntegerField('排序', unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
