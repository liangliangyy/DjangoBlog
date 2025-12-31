"""
可复用的测试基类和工具
提供通用的测试数据创建和断言方法
"""
from django.contrib.auth.models import Permission
from django.test import TestCase, Client, RequestFactory
from django.utils import timezone

from accounts.models import BlogUser
from blog.models import Article, Category, Tag, BlogSettings
from comments.models import Comment


class BaseTestCase(TestCase):
    """
    通用测试基类
    提供常用的测试数据创建方法
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = self.create_user()
        self.admin_user = self.create_admin_user()
        self.category = self.create_category()
        self.tag = self.create_tag()
        self.article = self.create_article()
        self.blog_settings = self.create_blog_settings()

    def create_user(self, username='testuser', email='test@test.com', password='testpass123'):
        """创建普通用户"""
        user = BlogUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user

    def create_admin_user(self, username='admin', email='admin@admin.com', password='admin123'):
        """创建管理员用户"""
        user = BlogUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        return user

    def create_staff_user(self, username='staff', email='staff@test.com', password='staff123'):
        """创建员工用户"""
        user = BlogUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        return user

    def create_category(self, name='测试分类'):
        """创建分类"""
        category = Category.objects.create(
            name=name,
            creation_time=timezone.now(),
            last_modify_time=timezone.now()
        )
        return category

    def create_tag(self, name='测试标签'):
        """创建标签"""
        tag = Tag.objects.create(name=name)
        return tag

    def create_article(self, title='测试文章', body='测试内容', author=None,
                      category=None, status='p', article_type='a'):
        """创建文章"""
        if author is None:
            author = self.user if hasattr(self, 'user') else self.create_user()
        if category is None:
            category = self.category if hasattr(self, 'category') else self.create_category()

        article = Article.objects.create(
            title=title,
            body=body,
            author=author,
            category=category,
            type=article_type,
            status=status
        )
        return article

    def create_comment(self, article=None, author=None, body='测试评论', parent=None):
        """创建评论"""
        if article is None:
            article = self.article if hasattr(self, 'article') else self.create_article()
        if author is None:
            author = self.user if hasattr(self, 'user') else self.create_user()

        comment = Comment.objects.create(
            body=body,
            author=author,
            article=article,
            parent_comment=parent
        )
        return comment

    def create_blog_settings(self):
        """创建博客设置"""
        settings, created = BlogSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': '测试博客',
                'site_description': '测试描述',
                'comment_need_review': False,
            }
        )
        return settings

    def login_user(self, user=None, password='testpass123'):
        """登录用户"""
        if user is None:
            user = self.user
        return self.client.login(username=user.username, password=password)

    def login_admin(self):
        """登录管理员"""
        return self.client.login(username='admin', password='admin123')

    def assert_redirect_to_login(self, response):
        """断言重定向到登录页"""
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def assert_permission_denied(self, response):
        """断言权限拒绝"""
        self.assertIn(response.status_code, [403, 302])


class ViewTestMixin:
    """
    视图测试混入类
    提供视图测试的通用方法
    """

    def assert_view_success(self, url, status_code=200):
        """断言视图访问成功"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        return response

    def assert_view_redirect(self, url, redirect_url=None):
        """断言视图重定向"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        if redirect_url:
            self.assertRedirects(response, redirect_url)
        return response

    def assert_view_forbidden(self, url):
        """断言视图禁止访问"""
        response = self.client.get(url)
        self.assertIn(response.status_code, [403, 302])
        return response

    def assert_post_success(self, url, data, status_code=200):
        """断言 POST 请求成功"""
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        return response

    def assert_ajax_success(self, url, data=None):
        """断言 AJAX 请求成功"""
        response = self.client.post(
            url,
            data or {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        return response


class AdminTestMixin:
    """
    Admin 测试混入类
    提供 Admin 测试的通用方法
    """

    def get_admin_url(self, model, action='changelist'):
        """获取 Admin URL"""
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        from django.urls import reverse
        return reverse(f'admin:{app_label}_{model_name}_{action}')

    def get_admin_change_url(self, obj):
        """获取对象的 Admin 修改 URL"""
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        from django.urls import reverse
        return reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])

    def assert_admin_accessible(self, model):
        """断言管理员可以访问 Admin 页面"""
        url = self.get_admin_url(model)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response

    def assert_admin_forbidden_for_user(self, model):
        """断言普通用户无法访问 Admin 页面"""
        url = self.get_admin_url(model)
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])
        return response


class PluginTestMixin:
    """
    插件测试混入类
    提供插件测试的通用方法
    """

    def create_plugin_context(self, **kwargs):
        """创建插件上下文"""
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = kwargs.get('user', self.user if hasattr(self, 'user') else None)

        context = {
            'request': request,
            'article': kwargs.get('article', None),
            'content': kwargs.get('content', ''),
        }
        return context

    def assert_plugin_hook_registered(self, plugin, hook_name):
        """断言插件钩子已注册"""
        from djangoblog.plugin_manage import hooks
        registered_hooks = hooks._hooks.get(hook_name, [])
        self.assertTrue(len(registered_hooks) > 0, f"No hooks registered for {hook_name}")

    def mock_plugin_config(self, plugin_name, **config):
        """Mock 插件配置"""
        import os
        for key, value in config.items():
            os.environ[key] = str(value)


class MockExternalService:
    """
    外部服务 Mock 工具
    提供常用外部服务的 Mock
    """

    @staticmethod
    def mock_http_response(status_code=200, content='', json_data=None):
        """Mock HTTP 响应"""
        from unittest.mock import Mock
        response = Mock()
        response.status_code = status_code
        response.content = content
        if json_data:
            response.json.return_value = json_data
        return response

    @staticmethod
    def mock_elasticsearch_response(hits=None):
        """Mock Elasticsearch 响应"""
        from unittest.mock import Mock
        response = Mock()
        response.hits = hits or []
        response.hits.total = Mock()
        response.hits.total.value = len(hits) if hits else 0
        return response

    @staticmethod
    def mock_cache_get(return_value=None):
        """Mock 缓存获取"""
        from unittest.mock import patch
        return patch('django.core.cache.cache.get', return_value=return_value)

    @staticmethod
    def mock_cache_set():
        """Mock 缓存设置"""
        from unittest.mock import patch
        return patch('django.core.cache.cache.set')
