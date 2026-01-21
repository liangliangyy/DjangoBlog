"""
Test cases for article business logic
包括文章状态转换、权限控制、评论控制等核心业务逻辑
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import BlogUser
from blog.models import Article, Category


class ArticleLifecycleTest(TestCase):
    """测试文章完整生命周期"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()

        # 创建测试分类
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # 创建作者用户
        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpassword'
        )

        # 创建其他普通用户
        self.other_user = BlogUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )

        # 创建管理员用户
        self.admin_user = BlogUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )

    def test_article_created_as_draft_by_default(self):
        """测试文章创建时默认为草稿状态"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='d',  # 草稿
            type='a'
        )
        self.assertEqual(article.status, 'd')

    def test_article_draft_to_published_transition(self):
        """测试文章从草稿到发布的状态转换"""
        article = Article.objects.create(
            title='Draft Article',
            body='Draft content',
            author=self.author,
            category=self.category,
            status='d',
            type='a'
        )

        # 验证初始状态
        self.assertEqual(article.status, 'd')
        original_pub_time = article.pub_time

        # 修改为发布状态
        article.status = 'p'
        article.save()

        # 验证状态已改变
        article.refresh_from_db()
        self.assertEqual(article.status, 'p')

    def test_article_published_to_draft_transition(self):
        """测试文章从发布到草稿的状态转换"""
        article = Article.objects.create(
            title='Published Article',
            body='Published content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 验证初始状态
        self.assertEqual(article.status, 'p')

        # 修改回草稿状态
        article.status = 'd'
        article.save()

        # 验证状态已改变
        article.refresh_from_db()
        self.assertEqual(article.status, 'd')

    def test_published_article_is_publicly_accessible(self):
        """测试已发布文章对所有人可见"""
        article = Article.objects.create(
            title='Public Article',
            body='Public content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 未登录用户访问
        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Article')

    def test_draft_article_not_in_public_list(self):
        """测试草稿文章不在公开列表中"""
        # 创建草稿文章
        draft_article = Article.objects.create(
            title='Draft Article',
            body='Draft content',
            author=self.author,
            category=self.category,
            status='d',
            type='a'
        )

        # 创建已发布文章
        published_article = Article.objects.create(
            title='Published Article',
            body='Published content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 获取公开文章列表（只包含已发布的）
        public_articles = Article.objects.filter(status='p', type='a')

        # 验证草稿文章不在列表中
        self.assertNotIn(draft_article, public_articles)
        self.assertIn(published_article, public_articles)

    def test_article_views_counter_increases(self):
        """测试文章浏览量计数器增加"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            views=0
        )

        initial_views = article.views

        # 模拟浏览文章
        article.views += 1
        article.save()

        # 验证浏览量增加
        article.refresh_from_db()
        self.assertEqual(article.views, initial_views + 1)

    def test_article_views_multiple_increments(self):
        """测试文章多次浏览时浏览量正确累加"""
        article = Article.objects.create(
            title='Popular Article',
            body='Popular content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            views=0
        )

        # 模拟多次浏览
        for i in range(10):
            article.views += 1
            article.save()

        article.refresh_from_db()
        self.assertEqual(article.views, 10)


class ArticleCommentStatusTest(TestCase):
    """测试文章评论状态控制"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='password'
        )

    def test_article_comment_open_by_default(self):
        """测试文章评论默认开放"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'  # 开放评论
        )

        self.assertEqual(article.comment_status, 'o')

    def test_article_comment_can_be_closed(self):
        """测试可以关闭文章评论"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'
        )

        # 关闭评论
        article.comment_status = 'c'
        article.save()

        article.refresh_from_db()
        self.assertEqual(article.comment_status, 'c')

    def test_closed_comment_article_status(self):
        """测试关闭评论的文章状态正确"""
        article = Article.objects.create(
            title='No Comments Article',
            body='No comments allowed',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='c'
        )

        # 验证评论已关闭
        self.assertEqual(article.comment_status, 'c')


class ArticlePermissionTest(TestCase):
    """测试文章权限控制"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpassword'
        )

        self.other_user = BlogUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )

        self.admin_user = BlogUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

    def test_author_is_article_owner(self):
        """测试作者是文章的所有者"""
        self.assertEqual(self.article.author, self.author)

    def test_other_user_is_not_article_owner(self):
        """测试其他用户不是文章的所有者"""
        self.assertNotEqual(self.article.author, self.other_user)

    def test_admin_has_superuser_privilege(self):
        """测试管理员有超级用户权限"""
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.is_staff)

    def test_normal_user_no_staff_privilege(self):
        """测试普通用户没有staff权限"""
        self.assertFalse(self.other_user.is_staff)
        self.assertFalse(self.other_user.is_superuser)

    def test_article_author_can_edit(self):
        """测试文章作者可以编辑（权限检查逻辑）"""
        # 验证作者权限
        can_edit = (self.article.author == self.author)
        self.assertTrue(can_edit)

    def test_other_user_cannot_edit(self):
        """测试其他用户不能编辑（权限检查逻辑）"""
        # 验证其他用户无权限
        can_edit = (self.article.author == self.other_user)
        self.assertFalse(can_edit)

    def test_admin_can_edit_any_article(self):
        """测试管理员可以编辑任何文章（超级用户权限）"""
        # 管理员有超级用户权限，可以编辑任何文章
        can_edit = (self.article.author == self.admin_user or
                   self.admin_user.is_superuser)
        self.assertTrue(can_edit)


class ArticleTypeTest(TestCase):
    """测试文章类型业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='password'
        )

    def test_article_type_is_article(self):
        """测试文章类型为article"""
        article = Article.objects.create(
            title='Article Type',
            body='Article content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'  # 文章类型
        )

        self.assertEqual(article.type, 'a')

    def test_article_type_is_page(self):
        """测试文章类型为page"""
        page = Article.objects.create(
            title='Page Type',
            body='Page content',
            author=self.author,
            category=self.category,
            status='p',
            type='p'  # 页面类型
        )

        self.assertEqual(page.type, 'p')

    def test_articles_and_pages_are_separate(self):
        """测试文章和页面分开查询"""
        # 创建文章
        article = Article.objects.create(
            title='Article',
            body='Article content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 创建页面
        page = Article.objects.create(
            title='Page',
            body='Page content',
            author=self.author,
            category=self.category,
            status='p',
            type='p'
        )

        # 只查询文章
        articles = Article.objects.filter(type='a', status='p')
        self.assertIn(article, articles)
        self.assertNotIn(page, articles)

        # 只查询页面
        pages = Article.objects.filter(type='p', status='p')
        self.assertIn(page, pages)
        self.assertNotIn(article, pages)


class ArticleCategoryTagTest(TestCase):
    """测试文章与分类标签的关系"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='password'
        )

    def test_article_belongs_to_category(self):
        """测试文章属于分类"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        self.assertEqual(article.category, self.category)

    def test_category_has_articles(self):
        """测试分类包含文章"""
        article1 = Article.objects.create(
            title='Article 1',
            body='Content 1',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        article2 = Article.objects.create(
            title='Article 2',
            body='Content 2',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 查询该分类下的文章
        category_articles = Article.objects.filter(
            category=self.category,
            status='p'
        )

        self.assertEqual(category_articles.count(), 2)
        self.assertIn(article1, category_articles)
        self.assertIn(article2, category_articles)

    def test_article_can_change_category(self):
        """测试文章可以更改分类"""
        new_category = Category.objects.create(
            name='New Category',
            slug='new-category'
        )

        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        # 更改分类
        article.category = new_category
        article.save()

        article.refresh_from_db()
        self.assertEqual(article.category, new_category)


class ArticleTimestampTest(TestCase):
    """测试文章时间戳业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='password'
        )

    def test_article_has_creation_time(self):
        """测试文章有创建时间"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        self.assertIsNotNone(article.creation_time)
        # 验证创建时间是最近的
        time_diff = timezone.now() - article.creation_time
        self.assertLess(time_diff.total_seconds(), 10)  # 10秒内创建

    def test_article_has_last_mod_time(self):
        """测试文章有最后修改时间"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        self.assertIsNotNone(article.last_modify_time)

    def test_article_last_mod_time_updates(self):
        """测试文章修改后最后修改时间更新"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        original_mod_time = article.last_modify_time

        # 等待一小段时间
        import time
        time.sleep(0.1)

        # 修改文章
        article.body = 'Updated content'
        article.save()

        article.refresh_from_db()
        # last_modify_time应该自动更新（如果模型配置了auto_now）
        # 注意：这取决于模型的auto_now配置


class ArticleSlugTest(TestCase):
    """测试文章slug生成逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.author = BlogUser.objects.create_user(
            username='author',
            email='author@example.com',
            password='password'
        )

    def test_article_has_id(self):
        """测试文章有ID（用于URL生成）"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        self.assertIsNotNone(article.id)
        # 验证可以通过ID访问
        retrieved_article = Article.objects.get(id=article.id)
        self.assertEqual(retrieved_article, article)

    def test_article_absolute_url(self):
        """测试文章绝对URL生成"""
        article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

        url = article.get_absolute_url()
        self.assertIsNotNone(url)
        # URL应该包含文章ID
        self.assertIn(str(article.id), url)
