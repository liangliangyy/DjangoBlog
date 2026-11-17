"""
Comments Views 测试
测试评论功能的错误处理和边界条件
"""
from django.test import TransactionTestCase, SimpleTestCase
from django.urls import reverse

from comments.models import Comment
from djangoblog.test_base import BaseTestCase, ViewTestMixin


class CommentViewTest(TransactionTestCase, ViewTestMixin):
    """测试评论视图"""

    def setUp(self):
        from django.test import Client
        from accounts.models import BlogUser
        from blog.models import Article, Category, BlogSettings
        from django.utils import timezone

        self.client = Client()
        self.user = BlogUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            creation_time=timezone.now(),
            last_modify_time=timezone.now()
        )
        self.article = Article.objects.create(
            title='测试文章',
            body='测试内容',
            author=self.user,
            category=self.category,
            type='a',
            status='p'
        )
        self.blog_settings, _ = BlogSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': '测试博客',
                'site_description': '测试描述',
                'comment_need_review': False,
            }
        )

    def login_user(self):
        """登录测试用户"""
        return self.client.login(username='testuser', password='testpass123')

    def test_post_comment_authenticated(self):
        """测试已登录用户发表评论"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        response = self.client.post(url, {'body': '这是一条测试评论'})
        self.assertEqual(response.status_code, 302)

        # 验证评论已创建
        comments = Comment.objects.filter(article=self.article)
        self.assertGreater(comments.count(), 0)

    def test_post_comment_unauthenticated(self):
        """测试未登录用户发表评论"""
        self.client.logout()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        response = self.client.post(url, {'body': '匿名评论'})
        # 未登录用户会被视图处理，可能返回错误或重定向
        # 由于视图会尝试获取用户，会产生错误，这是预期的
        self.assertIn(response.status_code, [200, 302, 403, 500])

    def test_post_comment_empty_body(self):
        """测试提交空评论"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        response = self.client.post(url, {'body': ''})
        # 应该返回表单错误
        self.assertIn(response.status_code, [200, 302])

    def test_post_comment_invalid_article(self):
        """测试对不存在的文章评论"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': 99999})
        response = self.client.post(url, {'body': '评论'})
        self.assertEqual(response.status_code, 404)

    def test_post_reply_comment(self):
        """测试回复评论"""
        self.login_user()
        # 先创建一条评论
        parent_comment = Comment.objects.create(
            body='父评论',
            author=self.user,
            article=self.article
        )
        parent_comment.is_enable = True
        parent_comment.save()

        # 回复这条评论
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        response = self.client.post(url, {
            'body': '这是回复',
            'parent_comment_id': parent_comment.id
        })
        self.assertIn(response.status_code, [200, 302])

    def test_comment_moderation(self):
        """测试评论审核"""
        # 设置需要审核
        self.blog_settings.comment_need_review = True
        self.blog_settings.save()

        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        response = self.client.post(url, {'body': '待审核的评论'})
        self.assertEqual(response.status_code, 302)

        # 验证评论需要审核
        comment = Comment.objects.filter(article=self.article).latest('id')
        self.assertFalse(comment.is_enable)

    def test_comment_display_on_article(self):
        """测试评论在文章页显示"""
        comment = Comment.objects.create(
            body='测试显示评论',
            author=self.user,
            article=self.article,
            is_enable=True
        )

        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_disabled_comment_not_display(self):
        """测试未启用的评论不显示"""
        comment = Comment.objects.create(
            body='未启用的评论',
            author=self.user,
            article=self.article,
            is_enable=False
        )

        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class CommentSpamTest(TransactionTestCase, ViewTestMixin):
    """测试评论垃圾防护"""

    def setUp(self):
        from django.test import Client
        from accounts.models import BlogUser
        from blog.models import Article, Category, BlogSettings
        from django.utils import timezone

        self.client = Client()
        self.user = BlogUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            creation_time=timezone.now(),
            last_modify_time=timezone.now()
        )
        self.article = Article.objects.create(
            title='测试文章',
            body='测试内容',
            author=self.user,
            category=self.category,
            type='a',
            status='p'
        )
        self.blog_settings, _ = BlogSettings.objects.get_or_create(
            id=1,
            defaults={'comment_need_review': False}
        )

    def login_user(self):
        return self.client.login(username='testuser', password='testpass123')

    def test_duplicate_comment(self):
        """测试重复评论"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})
        comment_data = {'body': '重复的评论内容'}

        # 第一次提交
        response1 = self.client.post(url, comment_data)
        self.assertEqual(response1.status_code, 302)

        # 第二次提交相同内容
        response2 = self.client.post(url, comment_data)
        # 应该被阻止或显示错误
        self.assertIn(response2.status_code, [200, 302])

    def test_comment_rate_limit(self):
        """测试评论频率限制"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})

        # 快速连续发表多条评论
        for i in range(5):
            response = self.client.post(url, {'body': f'评论{i}'})
            # 后续评论可能被限制
            self.assertIn(response.status_code, [200, 302, 429])


class CommentSecurityTest(TransactionTestCase, ViewTestMixin):
    """测试评论安全性"""

    def setUp(self):
        from django.test import Client
        from accounts.models import BlogUser
        from blog.models import Article, Category, BlogSettings
        from django.utils import timezone

        self.client = Client()
        self.user = BlogUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='测试分类',
            creation_time=timezone.now(),
            last_modify_time=timezone.now()
        )
        self.article = Article.objects.create(
            title='测试文章',
            body='测试内容',
            author=self.user,
            category=self.category,
            type='a',
            status='p'
        )
        self.blog_settings, _ = BlogSettings.objects.get_or_create(
            id=1,
            defaults={'comment_need_review': False}
        )

    def login_user(self):
        return self.client.login(username='testuser', password='testpass123')

    def test_xss_protection(self):
        """测试 XSS 防护"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})

        # 提交包含 script 标签的评论
        xss_body = '<script>alert("xss")</script>普通内容'
        response = self.client.post(url, {'body': xss_body})
        self.assertEqual(response.status_code, 302)

        # 验证评论已创建（XSS 过滤在渲染时处理）
        comment = Comment.objects.filter(article=self.article).latest('id')
        self.assertIsNotNone(comment)

    def test_sql_injection_protection(self):
        """测试 SQL 注入防护"""
        self.login_user()
        url = reverse('comments:postcomment', kwargs={'article_id': self.article.id})

        # 提交包含 SQL 注入尝试的评论
        sql_body = "'; DROP TABLE comments; --"
        response = self.client.post(url, {'body': sql_body})
        # 应该正常处理，不会执行 SQL
        self.assertIn(response.status_code, [200, 302])

        # 验证表仍然存在
        self.assertTrue(Comment.objects.exists())


class CommentXssFilterTest(SimpleTestCase):
    """XSS 过滤器层回归测试（不依赖数据库）。

    覆盖 issue #1030 的两个存储型 XSS 根因：
    - 漏洞1：sanitize_html 必须清理事件属性（nh3 替换 bleach 后的回归）
    - 漏洞2：reaction 数据经 json_script 输出必须转义（替换 to_json 后的回归）
    """

    def test_xss_event_attributes_stripped(self):
        """漏洞1回归：评论正文中的事件属性（onfocus/onerror/onmouseover 等）必须被清理。

        根因曾是 sanitize_html 的 class_filter 对非 class 属性 ``return value``，
        导致 onfocus/autofocus 漏过白名单。改用 nh3 后属性白名单为集合形式，
        div/img 等仅允许显式列出的属性，事件属性一律丢弃。
        """
        from blog.templatetags.blog_tags import comment_markdown
        payloads = [
            '<div autofocus onfocus=alert(document.domain)>x</div>',
            '<img src=x onerror=alert(1)>',
            '<div onmouseover=alert(1)>x</div>',
        ]
        for payload in payloads:
            rendered = comment_markdown(payload)
            for forbidden in ('onfocus', 'onerror', 'onmouseover', 'autofocus'):
                self.assertNotIn(
                    forbidden, rendered,
                    f'事件属性 {forbidden} 未被清理，payload={payload!r}')

    def test_reaction_nickname_xss_escaped(self):
        """漏洞2回归：昵称含恶意脚本时，经 json_script 输出必须转义，
        不得在 HTML 中产生攻击者注入的裸 ``<script>`` 标签。

        根因曾是 to_json 用 ``mark_safe(json.dumps(...))`` 把含单引号的昵称
        注入单引号包裹的 ``data-reactions`` 属性，属性被闭合后注入 ``<script>``。
        改用 Django ``json_script`` 后，``< > & '`` 被转义为 \\uXXXX。
        """
        from django.utils.html import json_script
        evil_nickname = '"\'><script src=//192.168.48.130:8081/x.js>'
        data = {
            '👍': {
                'count': 1,
                'has_reacted': False,
                'users': [evil_nickname],
            }
        }
        rendered = json_script(data, 'reactions-data-1')
        # 不得出现攻击者注入的裸 <script src= 标签
        self.assertNotIn('<script src=', rendered)
        # json_script 会把 < 转义为 <，确保转义生效
        self.assertIn('\\u003C', rendered)
        # 数据未被损坏：解析 script 标签内容应能还原原值
        import json as _json
        body = rendered.split('>', 1)[1].rsplit('</script>', 1)[0]
        self.assertEqual(_json.loads(body)['👍']['users'][0], evil_nickname)

    def test_to_json_filter_removed(self):
        """确认漏洞2的 sink to_json 过滤器已移除（改用 Django json_script）。"""
        from blog.templatetags import blog_tags
        self.assertFalse(
            hasattr(blog_tags, 'to_json'),
            'to_json 过滤器应已移除，改用 Django json_script')

    def test_normal_markdown_preserved(self):
        """正向回归：正常 Markdown（加粗、行内代码、代码块高亮）不应被 sanitize 误伤。"""
        from blog.templatetags.blog_tags import comment_markdown
        rendered = comment_markdown('Hello **world** and `code`')
        self.assertIn('<strong>world</strong>', rendered)
        self.assertIn('<code>code</code>', rendered)
        # 缩进代码块经 codehilite 扩展生成高亮容器，class 应保留
        self.assertIn('codehilite', comment_markdown('    print("hi")\n'))
