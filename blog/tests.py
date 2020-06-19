from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag, SideBar, Links
from django.contrib.auth import get_user_model
from DjangoBlog.utils import get_current_site, get_md5
from blog.forms import BlogSearchForm
from django.core.paginator import Paginator
from blog.templatetags.blog_tags import load_pagination_info, load_articletags
from accounts.models import BlogUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import os


# Create your tests here.

class ArticleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_article(self):
        site = get_current_site().domain
        user = BlogUser.objects.get_or_create(
            email="liangliangyy@gmail.com",
            username="liangliangyy")[0]
        user.set_password("liangliangyy")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        response = self.client.get(user.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/servermanager/emailsendlog/')
        response = self.client.get('admin/admin/logentry/')
        s = SideBar()
        s.sequence = 1
        s.name = 'test'
        s.content = 'test content'
        s.is_enable = True
        s.save()

        category = Category()
        category.name = "category"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
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

        for i in range(20):
            article = Article()
            article.title = "nicetitle" + str(i)
            article.body = "nicetitle" + str(i)
            article.author = user
            article.category = category
            article.type = 'a'
            article.status = 'p'
            article.save()
            article.tags.add(tag)
            article.save()
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

        rsp = self.client.get('/refresh')
        self.assertEqual(rsp.status_code, 302)

        self.client.login(username='liangliangyy', password='liangliangyy')
        rsp = self.client.get('/refresh')
        self.assertEqual(rsp.status_code, 200)

        response = self.client.get(reverse('blog:archives'))
        self.assertEqual(response.status_code, 200)

        p = Paginator(Article.objects.all(), 2)
        self.__check_pagination__(p, '', '')

        p = Paginator(Article.objects.filter(tags=tag), 2)
        self.__check_pagination__(p, '分类标签归档', tag.slug)

        p = Paginator(
            Article.objects.filter(
                author__username='liangliangyy'), 2)
        self.__check_pagination__(p, '作者文章归档', 'liangliangyy')

        p = Paginator(Article.objects.filter(category=category), 2)
        self.__check_pagination__(p, '分类目录归档', category.slug)

        f = BlogSearchForm()
        f.search()
        self.client.login(username='liangliangyy', password='liangliangyy')
        from DjangoBlog.spider_notify import SpiderNotify
        SpiderNotify.baidu_notify([article.get_full_url()])

        from blog.templatetags.blog_tags import gravatar_url, gravatar
        u = gravatar_url('liangliangyy@gmail.com')
        u = gravatar('liangliangyy@gmail.com')

        link = Links(
            sequence=1,
            name="lylinux",
            link='https://wwww.lylinux.net')
        link.save()
        response = self.client.get('/links.html')
        self.assertEqual(response.status_code, 200)

    def __check_pagination__(self, p, type, value):
        s = load_pagination_info(p.page(1), type, value)
        self.assertIsNotNone(s)
        response = self.client.get(s['previous_url'])
        self.assertEqual(response.status_code, 200)
        response = self.client.get(s['next_url'])
        self.assertEqual(response.status_code, 200)

        s = load_pagination_info(p.page(2), type, value)
        self.assertIsNotNone(s)
        response = self.client.get(s['previous_url'])
        self.assertEqual(response.status_code, 200)
        response = self.client.get(s['next_url'])
        self.assertEqual(response.status_code, 200)

    def test_validate_feed(self):
        user = BlogUser.objects.get_or_create(
            email="liangliangyy12@gmail.com",
            username="liangliangyy")[0]
        user.set_password("liangliangyy")
        user.save()
        self.client.login(username='liangliangyy', password='liangliangyy')

        rsp = self.client.get('/refresh')
        self.assertEqual(rsp.status_code, 403)

        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

    def test_image(self):
        import requests
        rsp = requests.get(
            'https://www.python.org/static/img/python-logo@2x.png')
        imagepath = os.path.join(settings.BASE_DIR, 'python.png')
        with open(imagepath, 'wb') as file:
            file.write(rsp.content)
        rsp = self.client.post('/upload')
        self.assertEqual(rsp.status_code, 403)
        sign = get_md5(get_md5(settings.SECRET_KEY))
        with open(imagepath, 'rb') as file:
            imgfile = SimpleUploadedFile(
                'python.png', file.read(), content_type='image/jpg')
            form_data = {'python.png': imgfile}
            rsp = self.client.post(
                '/upload?sign=' + sign, form_data, follow=True)

            self.assertEqual(rsp.status_code, 200)
        from DjangoBlog.utils import save_user_avatar, send_email
        send_email(['qq@qq.com'], 'testTitle', 'testContent')
        save_user_avatar(
            'https://www.python.org/static/img/python-logo@2x.png')
        """
        data = SimpleUploadedFile(imagepath, b'file_content', content_type='image/jpg')
        rsp = self.client.post('/upload', {'django.jpg': data})
        self.assertEqual(rsp.status_code, 200)
        SimpleUploadedFile()
        """

    def test_errorpage(self):
        rsp = self.client.get('/eee')
        self.assertEqual(rsp.status_code, 404)
