from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from blog.forms import BlogSearchForm
from django.core.paginator import Paginator
from blog.templatetags.blog_tags import load_pagination_info, load_articletags
import datetime
from accounts.models import BlogUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os


# Create your tests here.

class ArticleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_article(self):
        site = Site.objects.get_current().domain
        user = BlogUser.objects.get_or_create(email="liangliangyy@gmail.com", username="liangliangyy")[0]
        user.set_password("liangliangyy")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        response = self.client.get(user.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        category = Category()
        category.name = "category"
        category.created_time = datetime.datetime.now()
        category.last_mod_time = datetime.datetime.now()
        category.save()

        tag = Tag()
        tag.name = "nicetag"
        tag.save()

        article = Article()
        article.title = "nicetitle"
        article.body = "nicecontent"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'

        article.save()
        self.assertEqual(0, article.tags.count())
        article.tags.add(tag)
        article.save()
        self.assertEqual(1, article.tags.count())

        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        from DjangoBlog.spider_notify import SpiderNotify
        SpiderNotify.notify(article.get_absolute_url())
        response = self.client.get(tag.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(category.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search', {'q': 'django'})
        self.assertEqual(response.status_code, 200)
        s = load_articletags(article)
        self.assertIsNotNone(s)

        p = Paginator(Article.objects.all(), 2)
        s = load_pagination_info(p.page(1), '', '')
        self.assertIsNotNone(s)

        p = Paginator(Tag.objects.all(), 2)
        s = load_pagination_info(p.page(1), '分类标签归档', 'tagname')
        self.assertIsNotNone(s)

        p = Paginator(BlogUser.objects.all(), 2)
        s = load_pagination_info(p.page(1), '作者文章归档', 'username')
        self.assertIsNotNone(s)

        p = Paginator(Category.objects.all(), 2)
        s = load_pagination_info(p.page(1), '分类目录归档', 'categoryname')
        self.assertIsNotNone(s)

        f = BlogSearchForm()
        f.search()
        self.client.login(username='liangliangyy', password='liangliangyy')
        from DjangoBlog.spider_notify import SpiderNotify
        SpiderNotify.baidu_notify([article.get_full_url()])
        rsp = self.client.get('/refresh/')
        self.assertEqual(rsp.status_code, 200)
        from blog.templatetags.blog_tags import gravatar_url, gravatar
        u = gravatar_url('liangliangyy@gmail.com')
        u = gravatar('liangliangyy@gmail.com')

    def test_validate_feed(self):
        user = BlogUser.objects.get_or_create(email="liangliangyy12@gmail.com", username="liangliangyy")[0]
        user.set_password("liangliangyy")
        user.save()

        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

    def test_image(self):
        import requests
        rsp = requests.get('https://ss2.baidu.com/6ONYsjip0QIZ8tyhnq/it/u=2909203028,3998034658&fm=96')
        imagepath = os.path.join(settings.BASE_DIR, 'django.jpg')
        with open(imagepath, 'wb') as file:
            file.write(rsp.content)
        with open(imagepath, 'rb') as file:
            imgfile = SimpleUploadedFile('django.jpg', file.read(), content_type='image/jpg')
            form_data = {'django.jpg': imgfile}
            rsp = self.client.post('/upload', form_data, follow=True)

            self.assertEqual(rsp.status_code, 200)
        """
        data = SimpleUploadedFile(imagepath, b'file_content', content_type='image/jpg')
        rsp = self.client.post('/upload', {'django.jpg': data})
        self.assertEqual(rsp.status_code, 200)
        SimpleUploadedFile()
        """
    def test_errorpage(self):
        self.client.get('/eee')
        self.client.get('/refresh_memcache')
