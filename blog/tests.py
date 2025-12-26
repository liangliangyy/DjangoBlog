import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.paginator import Paginator
from django.templatetags.static import static
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import BlogUser
from blog.forms import BlogSearchForm
from blog.models import Article, Category, Tag, SideBar, Links
from blog.templatetags.blog_tags import load_pagination_info, load_articletags, highlight_search_term, highlight_content
from djangoblog.utils import get_current_site, get_sha256
from oauth.models import OAuthUser, OAuthConfig


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
        category.creation_time = timezone.now()
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
        from blog.documents import ELASTICSEARCH_ENABLED
        if ELASTICSEARCH_ENABLED:
            call_command("build_index")
            response = self.client.get('/search', {'q': 'nicetitle'})
            self.assertEqual(response.status_code, 200)

        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        from djangoblog.spider_notify import SpiderNotify
        SpiderNotify.notify(article.get_absolute_url())
        response = self.client.get(tag.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(category.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search', {'q': 'django'})
        self.assertEqual(response.status_code, 200)
        s = load_articletags(article)
        self.assertIsNotNone(s)

        self.client.login(username='liangliangyy', password='liangliangyy')

        response = self.client.get(reverse('blog:archives'))
        self.assertEqual(response.status_code, 200)

        p = Paginator(Article.objects.all(), settings.PAGINATE_BY)
        self.check_pagination(p, '', '')

        p = Paginator(Article.objects.filter(tags=tag), settings.PAGINATE_BY)
        self.check_pagination(p, '分类标签归档', tag.slug)

        p = Paginator(
            Article.objects.filter(
                author__username='liangliangyy'), settings.PAGINATE_BY)
        self.check_pagination(p, '作者文章归档', 'liangliangyy')

        p = Paginator(Article.objects.filter(category=category), settings.PAGINATE_BY)
        self.check_pagination(p, '分类目录归档', category.slug)

        f = BlogSearchForm()
        f.search()
        # self.client.login(username='liangliangyy', password='liangliangyy')
        from djangoblog.spider_notify import SpiderNotify
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

        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

        self.client.get("/admin/blog/article/1/delete/")
        self.client.get('/admin/servermanager/emailsendlog/')
        self.client.get('/admin/admin/logentry/')
        self.client.get('/admin/admin/logentry/1/change/')

    def check_pagination(self, p, type, value):
        for page in range(1, p.num_pages + 1):
            s = load_pagination_info(p.page(page), type, value)
            self.assertIsNotNone(s)
            if s['previous_url']:
                response = self.client.get(s['previous_url'])
                self.assertEqual(response.status_code, 200)
            if s['next_url']:
                response = self.client.get(s['next_url'])
                self.assertEqual(response.status_code, 200)

    def test_image(self):
        import requests
        rsp = requests.get(
            'https://www.python.org/static/img/python-logo.png')
        imagepath = os.path.join(settings.BASE_DIR, 'python.png')
        with open(imagepath, 'wb') as file:
            file.write(rsp.content)
        rsp = self.client.post('/upload')
        self.assertEqual(rsp.status_code, 403)
        sign = get_sha256(get_sha256(settings.SECRET_KEY))
        with open(imagepath, 'rb') as file:
            imgfile = SimpleUploadedFile(
                'python.png', file.read(), content_type='image/jpg')
            form_data = {'python.png': imgfile}
            rsp = self.client.post(
                '/upload?sign=' + sign, form_data, follow=True)
            self.assertEqual(rsp.status_code, 200)
        os.remove(imagepath)
        from djangoblog.utils import save_user_avatar, send_email
        send_email(['qq@qq.com'], 'testTitle', 'testContent')
        save_user_avatar(
            'https://www.python.org/static/img/python-logo.png')

    def test_errorpage(self):
        rsp = self.client.get('/eee')
        self.assertEqual(rsp.status_code, 404)

    def test_commands(self):
        user = BlogUser.objects.get_or_create(
            email="liangliangyy@gmail.com",
            username="liangliangyy")[0]
        user.set_password("liangliangyy")
        user.is_staff = True
        user.is_superuser = True
        user.save()

        c = OAuthConfig()
        c.type = 'qq'
        c.appkey = 'appkey'
        c.appsecret = 'appsecret'
        c.save()

        u = OAuthUser()
        u.type = 'qq'
        u.openid = 'openid'
        u.user = user
        u.picture = static("/blog/img/avatar.png")
        u.metadata = '''
{
"figureurl": "https://qzapp.qlogo.cn/qzapp/101513904/C740E30B4113EAA80E0D9918ABC78E82/30"
}'''
        u.save()

        u = OAuthUser()
        u.type = 'qq'
        u.openid = 'openid1'
        u.picture = 'https://qzapp.qlogo.cn/qzapp/101513904/C740E30B4113EAA80E0D9918ABC78E82/30'
        u.metadata = '''
        {
       "figureurl": "https://qzapp.qlogo.cn/qzapp/101513904/C740E30B4113EAA80E0D9918ABC78E82/30"
        }'''
        u.save()

        from blog.documents import ELASTICSEARCH_ENABLED
        if ELASTICSEARCH_ENABLED:
            call_command("build_index")
        call_command("ping_baidu", "all")
        call_command("create_testdata")
        call_command("clear_cache")
        call_command("sync_user_avatar")
        call_command("build_search_words")


class SearchHighlightTest(TestCase):
    """测试搜索高亮功能"""

    def test_highlight_search_term_filter(self):
        """测试标题高亮filter"""
        # 测试基本高亮
        text = "Django is a web framework"
        result = highlight_search_term(text, "django")
        self.assertIn("<mark>Django</mark>", result)
        self.assertIn("web framework", result)

        # 测试不区分大小写
        text = "Python and python"
        result = highlight_search_term(text, "PYTHON")
        self.assertEqual(result.count("<mark>"), 2)

        # 测试多个关键词
        text = "Django web framework with Python"
        result = highlight_search_term(text, "django python")
        self.assertIn("<mark>Django</mark>", result)
        self.assertIn("<mark>Python</mark>", result)

        # 测试空查询
        text = "Some text"
        result = highlight_search_term(text, "")
        self.assertEqual(result, text)

        # 测试空文本
        result = highlight_search_term("", "query")
        self.assertEqual(result, "")

    def test_highlight_content_filter(self):
        """测试正文高亮filter"""
        # 测试HTML内容高亮
        html = "<p>Django is a great web framework. Django makes development easy.</p>"
        result = highlight_content(html, "django")

        # 应该包含高亮标记
        self.assertIn("<mark>", result)
        self.assertIn("</mark>", result)

        # HTML标签应该被去除
        self.assertNotIn("<p>", result)

        # 应该包含Django关键词（不区分大小写）
        self.assertIn("django", result.lower())

        # 测试空查询
        result = highlight_content(html, "")
        self.assertEqual(result, html)

    def test_search_page_access(self):
        """测试搜索页面访问"""
        # 测试搜索页面可以正常访问
        response = self.client.get('/search', {'q': 'django'})
        self.assertEqual(response.status_code, 200)

        # 检查响应中是否有查询参数
        self.assertIn('query', response.context)
        self.assertEqual(response.context['query'], 'django')

    def test_chinese_keyword_highlight(self):
        """测试中文关键词高亮"""
        text = "这是一个Django博客系统"
        result = highlight_search_term(text, "Django")
        self.assertIn("<mark>Django</mark>", result)

        # 测试中文关键词
        text = "欢迎使用DjangoBlog系统"
        result = highlight_search_term(text, "Django")
        self.assertIn("<mark>Django</mark>", result)
