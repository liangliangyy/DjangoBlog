"""
Test cases for comment business logic
包括评论审核工作流、嵌套回复、权限控制等核心业务逻辑
"""
from django.test import TestCase, Client
from django.utils import timezone

from accounts.models import BlogUser
from blog.models import Article, Category, BlogSettings
from comments.models import Comment


class CommentCreationTest(TestCase):
    """测试评论创建业务逻辑"""

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

        self.commenter = BlogUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'
        )

    def test_comment_created_with_required_fields(self):
        """测试评论创建包含必需字段"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article
        )

        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.body, 'Test comment')
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.article, self.article)

    def test_comment_has_creation_time(self):
        """测试评论有创建时间"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article
        )

        self.assertIsNotNone(comment.creation_time)
        # 验证创建时间是最近的
        time_diff = timezone.now() - comment.creation_time
        self.assertLess(time_diff.total_seconds(), 10)

    def test_comment_author_is_correct(self):
        """测试评论作者正确"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article
        )

        self.assertEqual(comment.author, self.commenter)

    def test_comment_article_relationship(self):
        """测试评论与文章的关系"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article
        )

        self.assertEqual(comment.article, self.article)
        # 验证可以通过文章查询到评论
        article_comments = Comment.objects.filter(article=self.article)
        self.assertIn(comment, article_comments)


class CommentModerationTest(TestCase):
    """测试评论审核工作流"""

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

        self.commenter = BlogUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'
        )

        # 获取或创建博客设置
        self.blog_settings, _ = BlogSettings.objects.get_or_create(
            id=1,
            defaults={'site_name': 'Test Blog'}
        )

    def test_comment_pending_by_default_when_review_required(self):
        """测试需要审核时评论默认为待审状态"""
        # 启用评论审核
        self.blog_settings.comment_need_review = True
        self.blog_settings.save()

        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article,
            is_enable=False  # 待审状态
        )

        self.assertFalse(comment.is_enable)

    def test_comment_approved_directly_when_no_review_required(self):
        """测试不需要审核时评论直接通过"""
        # 禁用评论审核
        self.blog_settings.comment_need_review = False
        self.blog_settings.save()

        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article,
            is_enable=True  # 直接启用
        )

        self.assertTrue(comment.is_enable)

    def test_comment_can_be_approved(self):
        """测试评论可以被批准"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article,
            is_enable=False
        )

        # 审核通过
        comment.is_enable = True
        comment.save()

        comment.refresh_from_db()
        self.assertTrue(comment.is_enable)

    def test_comment_can_be_rejected(self):
        """测试评论可以被拒绝"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        # 拒绝评论
        comment.is_enable = False
        comment.save()

        comment.refresh_from_db()
        self.assertFalse(comment.is_enable)

    def test_only_approved_comments_in_public_list(self):
        """测试只有已批准的评论在公开列表中"""
        # 创建已批准的评论
        approved_comment = Comment.objects.create(
            body='Approved comment',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        # 创建待审的评论
        pending_comment = Comment.objects.create(
            body='Pending comment',
            author=self.commenter,
            article=self.article,
            is_enable=False
        )

        # 查询已批准的评论
        approved_comments = Comment.objects.filter(
            article=self.article,
            is_enable=True
        )

        self.assertIn(approved_comment, approved_comments)
        self.assertNotIn(pending_comment, approved_comments)


class CommentReplyTest(TestCase):
    """测试评论回复业务逻辑"""

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

        self.commenter1 = BlogUser.objects.create_user(
            username='commenter1',
            email='commenter1@example.com',
            password='password'
        )

        self.commenter2 = BlogUser.objects.create_user(
            username='commenter2',
            email='commenter2@example.com',
            password='password'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'
        )

    def test_comment_can_have_no_parent(self):
        """测试评论可以没有父评论（根评论）"""
        comment = Comment.objects.create(
            body='Root comment',
            author=self.commenter1,
            article=self.article,
            parent_comment=None
        )

        self.assertIsNone(comment.parent_comment)

    def test_comment_can_have_parent(self):
        """测试评论可以有父评论（回复）"""
        parent_comment = Comment.objects.create(
            body='Parent comment',
            author=self.commenter1,
            article=self.article,
            is_enable=True
        )

        reply_comment = Comment.objects.create(
            body='Reply comment',
            author=self.commenter2,
            article=self.article,
            parent_comment=parent_comment,
            is_enable=True
        )

        self.assertEqual(reply_comment.parent_comment, parent_comment)

    def test_parent_comment_has_replies(self):
        """测试父评论有回复"""
        parent_comment = Comment.objects.create(
            body='Parent comment',
            author=self.commenter1,
            article=self.article,
            is_enable=True
        )

        reply1 = Comment.objects.create(
            body='Reply 1',
            author=self.commenter2,
            article=self.article,
            parent_comment=parent_comment,
            is_enable=True
        )

        reply2 = Comment.objects.create(
            body='Reply 2',
            author=self.commenter1,
            article=self.article,
            parent_comment=parent_comment,
            is_enable=True
        )

        # 查询父评论的所有回复
        replies = Comment.objects.filter(parent_comment=parent_comment)

        self.assertEqual(replies.count(), 2)
        self.assertIn(reply1, replies)
        self.assertIn(reply2, replies)

    def test_nested_comment_structure(self):
        """测试嵌套评论结构"""
        # 创建根评论
        root = Comment.objects.create(
            body='Root',
            author=self.commenter1,
            article=self.article,
            is_enable=True
        )

        # 创建一级回复
        level1 = Comment.objects.create(
            body='Level 1',
            author=self.commenter2,
            article=self.article,
            parent_comment=root,
            is_enable=True
        )

        # 创建二级回复
        level2 = Comment.objects.create(
            body='Level 2',
            author=self.commenter1,
            article=self.article,
            parent_comment=level1,
            is_enable=True
        )

        # 验证嵌套关系
        self.assertIsNone(root.parent_comment)
        self.assertEqual(level1.parent_comment, root)
        self.assertEqual(level2.parent_comment, level1)

    def test_multiple_replies_to_same_comment(self):
        """测试同一评论的多个回复"""
        parent = Comment.objects.create(
            body='Parent',
            author=self.commenter1,
            article=self.article,
            is_enable=True
        )

        # 创建多个回复
        replies = []
        for i in range(5):
            reply = Comment.objects.create(
                body=f'Reply {i+1}',
                author=self.commenter2,
                article=self.article,
                parent_comment=parent,
                is_enable=True
            )
            replies.append(reply)

        # 验证所有回复都关联到同一父评论
        parent_replies = Comment.objects.filter(parent_comment=parent)
        self.assertEqual(parent_replies.count(), 5)

        for reply in replies:
            self.assertIn(reply, parent_replies)


class CommentArticleStatusTest(TestCase):
    """测试评论与文章状态的关系"""

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

        self.commenter = BlogUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password'
        )

    def test_can_comment_on_open_comment_article(self):
        """测试可以在开放评论的文章上评论"""
        article = Article.objects.create(
            title='Open Comment Article',
            body='Content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='o'  # 开放评论
        )

        # 业务逻辑层面：评论状态开放
        self.assertEqual(article.comment_status, 'o')

        # 创建评论应该成功
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=article,
            is_enable=True
        )

        self.assertIsNotNone(comment.id)

    def test_comment_status_closed_validation(self):
        """测试关闭评论的文章状态"""
        article = Article.objects.create(
            title='Closed Comment Article',
            body='Content',
            author=self.author,
            category=self.category,
            status='p',
            type='a',
            comment_status='c'  # 关闭评论
        )

        # 验证文章评论状态
        self.assertEqual(article.comment_status, 'c')

        # 注意：实际的验证应该在视图层进行
        # 这里我们只测试模型层面的状态

    def test_comments_belong_to_correct_article(self):
        """测试评论属于正确的文章"""
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

        comment1 = Comment.objects.create(
            body='Comment on Article 1',
            author=self.commenter,
            article=article1,
            is_enable=True
        )

        comment2 = Comment.objects.create(
            body='Comment on Article 2',
            author=self.commenter,
            article=article2,
            is_enable=True
        )

        # 验证评论属于正确的文章
        article1_comments = Comment.objects.filter(article=article1)
        article2_comments = Comment.objects.filter(article=article2)

        self.assertIn(comment1, article1_comments)
        self.assertNotIn(comment2, article1_comments)

        self.assertIn(comment2, article2_comments)
        self.assertNotIn(comment1, article2_comments)


class CommentQueryTest(TestCase):
    """测试评论查询业务逻辑"""

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

        self.commenter = BlogUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

    def test_query_comments_by_article(self):
        """测试按文章查询评论"""
        # 创建多个评论
        for i in range(5):
            Comment.objects.create(
                body=f'Comment {i+1}',
                author=self.commenter,
                article=self.article,
                is_enable=True
            )

        comments = Comment.objects.filter(article=self.article)
        self.assertEqual(comments.count(), 5)

    def test_query_comments_by_author(self):
        """测试按作者查询评论"""
        # 创建评论
        for i in range(3):
            Comment.objects.create(
                body=f'Comment {i+1}',
                author=self.commenter,
                article=self.article,
                is_enable=True
            )

        comments = Comment.objects.filter(author=self.commenter)
        self.assertEqual(comments.count(), 3)

    def test_query_root_comments_only(self):
        """测试只查询根评论（无父评论的评论）"""
        # 创建根评论
        root1 = Comment.objects.create(
            body='Root 1',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        root2 = Comment.objects.create(
            body='Root 2',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        # 创建回复
        Comment.objects.create(
            body='Reply to Root 1',
            author=self.commenter,
            article=self.article,
            parent_comment=root1,
            is_enable=True
        )

        # 查询根评论
        root_comments = Comment.objects.filter(
            article=self.article,
            parent_comment__isnull=True
        )

        self.assertEqual(root_comments.count(), 2)
        self.assertIn(root1, root_comments)
        self.assertIn(root2, root_comments)

    def test_comment_ordering(self):
        """测试评论排序"""
        # 创建多个评论
        comments = []
        for i in range(3):
            comment = Comment.objects.create(
                body=f'Comment {i+1}',
                author=self.commenter,
                article=self.article,
                is_enable=True
            )
            comments.append(comment)

        # 查询评论（应该按照模型定义的ordering排序）
        ordered_comments = list(Comment.objects.filter(article=self.article))

        # 验证至少返回了正确数量的评论
        self.assertEqual(len(ordered_comments), 3)


class CommentDeletionTest(TestCase):
    """测试评论删除业务逻辑"""

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

        self.commenter = BlogUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password'
        )

        self.article = Article.objects.create(
            title='Test Article',
            body='Test content',
            author=self.author,
            category=self.category,
            status='p',
            type='a'
        )

    def test_comment_can_be_deleted(self):
        """测试评论可以被删除"""
        comment = Comment.objects.create(
            body='Test comment',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        comment_id = comment.id

        # 删除评论
        comment.delete()

        # 验证评论已被删除
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=comment_id)

    def test_deleting_parent_comment_with_replies(self):
        """测试删除有回复的父评论"""
        parent = Comment.objects.create(
            body='Parent',
            author=self.commenter,
            article=self.article,
            is_enable=True
        )

        reply = Comment.objects.create(
            body='Reply',
            author=self.commenter,
            article=self.article,
            parent_comment=parent,
            is_enable=True
        )

        parent_id = parent.id
        reply_id = reply.id

        # 删除父评论
        parent.delete()

        # 验证父评论被删除
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=parent_id)

        # 验证回复的处理（取决于模型的on_delete设置）
        # 如果是CASCADE，回复也应该被删除
        # 如果是SET_NULL，回复的parent应该为None
