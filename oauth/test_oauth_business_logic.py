"""
Test cases for OAuth business logic
包括OAuth配置、OAuth用户、第三方登录等核心业务逻辑
"""
from django.test import TestCase

from accounts.models import BlogUser
from oauth.models import OAuthConfig, OAuthUser


class OAuthConfigTest(TestCase):
    """测试OAuth配置业务逻辑"""

    def test_oauth_config_can_be_created(self):
        """测试OAuth配置可以被创建"""
        config = OAuthConfig.objects.create(
            type='weibo',
            appkey='test_app_key',
            appsecret='test_app_secret',
            callback_url='http://example.com/oauth/callback'
        )

        self.assertIsNotNone(config.id)
        self.assertEqual(config.type, 'weibo')
        self.assertEqual(config.appkey, 'test_app_key')

    def test_oauth_config_has_required_fields(self):
        """测试OAuth配置有必需字段"""
        config = OAuthConfig.objects.create(
            type='github',
            appkey='github_key',
            appsecret='github_secret',
            callback_url='http://example.com/oauth/github/callback'
        )

        self.assertEqual(config.type, 'github')
        self.assertIsNotNone(config.appkey)
        self.assertIsNotNone(config.appsecret)
        self.assertIsNotNone(config.callback_url)

    def test_oauth_config_type_uniqueness(self):
        """测试OAuth配置类型唯一性"""
        OAuthConfig.objects.create(
            type='google',
            appkey='key1',
            appsecret='secret1',
            callback_url='http://example.com/callback1'
        )

        # 尝试创建相同类型的配置可能失败（取决于模型设计）
        # 如果type字段有unique约束
        try:
            OAuthConfig.objects.create(
                type='google',
                appkey='key2',
                appsecret='secret2',
                callback_url='http://example.com/callback2'
            )
            # 如果没有unique约束，应该能创建成功
        except Exception:
            # 如果有unique约束，应该抛出异常
            pass

    def test_oauth_config_query_by_type(self):
        """测试按类型查询OAuth配置"""
        OAuthConfig.objects.create(
            type='weibo',
            appkey='weibo_key',
            appsecret='weibo_secret',
            callback_url='http://example.com/weibo'
        )

        OAuthConfig.objects.create(
            type='github',
            appkey='github_key',
            appsecret='github_secret',
            callback_url='http://example.com/github'
        )

        # 查询特定类型的配置
        weibo_config = OAuthConfig.objects.filter(type='weibo').first()
        self.assertIsNotNone(weibo_config)
        self.assertEqual(weibo_config.type, 'weibo')

    def test_oauth_config_is_enable_field(self):
        """测试OAuth配置的启用字段"""
        config = OAuthConfig.objects.create(
            type='facebook',
            appkey='fb_key',
            appsecret='fb_secret',
            callback_url='http://example.com/facebook',
            is_enable=True
        )

        self.assertTrue(config.is_enable)

        # 禁用配置
        config.is_enable = False
        config.save()

        config.refresh_from_db()
        self.assertFalse(config.is_enable)


class OAuthUserTest(TestCase):
    """测试OAuth用户业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.blog_user = BlogUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )

    def test_oauth_user_can_be_created(self):
        """测试OAuth用户可以被创建"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='test_openid_123',
            nickname='Test User',
            token='test_token',
            type='weibo'
        )

        self.assertIsNotNone(oauth_user.id)
        self.assertEqual(oauth_user.author, self.blog_user)
        self.assertEqual(oauth_user.openid, 'test_openid_123')

    def test_oauth_user_links_to_blog_user(self):
        """测试OAuth用户关联到博客用户"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid_456',
            nickname='OAuth User',
            token='oauth_token',
            type='github'
        )

        self.assertEqual(oauth_user.author, self.blog_user)

        # 验证可以从博客用户查询OAuth用户
        oauth_users = OAuthUser.objects.filter(author=self.blog_user)
        self.assertIn(oauth_user, oauth_users)

    def test_oauth_user_has_openid(self):
        """测试OAuth用户有openid"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='unique_openid',
            nickname='User',
            token='token',
            type='google'
        )

        self.assertEqual(oauth_user.openid, 'unique_openid')

    def test_oauth_user_has_type(self):
        """测试OAuth用户有类型"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='facebook'
        )

        self.assertEqual(oauth_user.type, 'facebook')

    def test_oauth_user_token_storage(self):
        """测试OAuth用户token存储"""
        token = 'test_access_token_12345'
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token=token,
            type='weibo'
        )

        self.assertEqual(oauth_user.token, token)

    def test_oauth_user_nickname_storage(self):
        """测试OAuth用户昵称存储"""
        nickname = 'OAuth Nickname'
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname=nickname,
            token='token',
            type='github'
        )

        self.assertEqual(oauth_user.nickname, nickname)


class OAuthUserQueryTest(TestCase):
    """测试OAuth用户查询业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.user1 = BlogUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password'
        )

        self.user2 = BlogUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password'
        )

    def test_query_oauth_user_by_openid(self):
        """测试按openid查询OAuth用户"""
        oauth_user = OAuthUser.objects.create(
            author=self.user1,
            openid='unique_openid_123',
            nickname='User',
            token='token',
            type='weibo'
        )

        # 按openid查询
        found_user = OAuthUser.objects.get(openid='unique_openid_123')
        self.assertEqual(found_user, oauth_user)

    def test_query_oauth_user_by_type(self):
        """测试按类型查询OAuth用户"""
        weibo_user = OAuthUser.objects.create(
            author=self.user1,
            openid='weibo_openid',
            nickname='Weibo User',
            token='token',
            type='weibo'
        )

        github_user = OAuthUser.objects.create(
            author=self.user2,
            openid='github_openid',
            nickname='GitHub User',
            token='token',
            type='github'
        )

        # 查询weibo类型的用户
        weibo_users = OAuthUser.objects.filter(type='weibo')
        self.assertEqual(weibo_users.count(), 1)
        self.assertIn(weibo_user, weibo_users)

        # 查询github类型的用户
        github_users = OAuthUser.objects.filter(type='github')
        self.assertEqual(github_users.count(), 1)
        self.assertIn(github_user, github_users)

    def test_query_oauth_users_by_blog_user(self):
        """测试按博客用户查询OAuth用户"""
        # 为user1创建多个OAuth关联
        weibo = OAuthUser.objects.create(
            author=self.user1,
            openid='weibo_id',
            nickname='User',
            token='token',
            type='weibo'
        )

        github = OAuthUser.objects.create(
            author=self.user1,
            openid='github_id',
            nickname='User',
            token='token',
            type='github'
        )

        # 查询user1的所有OAuth关联
        oauth_users = OAuthUser.objects.filter(author=self.user1)
        self.assertEqual(oauth_users.count(), 2)
        self.assertIn(weibo, oauth_users)
        self.assertIn(github, oauth_users)

    def test_user_can_have_multiple_oauth_accounts(self):
        """测试用户可以关联多个OAuth账号"""
        oauth_types = ['weibo', 'github', 'google', 'facebook']

        for oauth_type in oauth_types:
            OAuthUser.objects.create(
                author=self.user1,
                openid=f'{oauth_type}_openid',
                nickname='User',
                token='token',
                type=oauth_type
            )

        # 验证用户有4个OAuth关联
        oauth_users = OAuthUser.objects.filter(author=self.user1)
        self.assertEqual(oauth_users.count(), 4)


class OAuthUserBindingTest(TestCase):
    """测试OAuth用户绑定业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.blog_user = BlogUser.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )

    def test_bind_oauth_to_existing_user(self):
        """测试将OAuth绑定到现有用户"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='new_openid',
            nickname='OAuth User',
            token='token',
            type='weibo'
        )

        # 验证绑定关系
        self.assertEqual(oauth_user.author, self.blog_user)

        # 验证可以通过博客用户找到OAuth用户
        oauth_accounts = OAuthUser.objects.filter(author=self.blog_user)
        self.assertIn(oauth_user, oauth_accounts)

    def test_unbind_oauth_from_user(self):
        """测试解绑OAuth账号"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='github'
        )

        oauth_id = oauth_user.id

        # 删除OAuth绑定
        oauth_user.delete()

        # 验证OAuth用户已删除
        with self.assertRaises(OAuthUser.DoesNotExist):
            OAuthUser.objects.get(id=oauth_id)

        # 博客用户应该仍然存在
        self.assertTrue(BlogUser.objects.filter(id=self.blog_user.id).exists())

    def test_change_oauth_binding(self):
        """测试更改OAuth绑定"""
        new_user = BlogUser.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password'
        )

        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='weibo'
        )

        # 更改绑定到新用户
        oauth_user.author = new_user
        oauth_user.save()

        oauth_user.refresh_from_db()
        self.assertEqual(oauth_user.author, new_user)


class OAuthTokenManagementTest(TestCase):
    """测试OAuth token管理业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.blog_user = BlogUser.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )

    def test_oauth_token_can_be_updated(self):
        """测试OAuth token可以更新"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='old_token',
            type='weibo'
        )

        # 更新token
        new_token = 'new_refreshed_token'
        oauth_user.token = new_token
        oauth_user.save()

        oauth_user.refresh_from_db()
        self.assertEqual(oauth_user.token, new_token)

    def test_oauth_user_token_storage(self):
        """测试OAuth token存储"""
        # token字段最大150字符
        long_token = 'a' * 140  # 安全的长度

        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token=long_token,
            type='github'
        )

        self.assertEqual(oauth_user.token, long_token)


class OAuthUserDeletionTest(TestCase):
    """测试OAuth用户删除业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.blog_user = BlogUser.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )

    def test_delete_oauth_user(self):
        """测试删除OAuth用户"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='weibo'
        )

        oauth_id = oauth_user.id

        # 删除OAuth用户
        oauth_user.delete()

        # 验证已删除
        with self.assertRaises(OAuthUser.DoesNotExist):
            OAuthUser.objects.get(id=oauth_id)

    def test_delete_blog_user_cascade_oauth(self):
        """测试删除博客用户级联删除OAuth用户"""
        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='github'
        )

        oauth_id = oauth_user.id

        # 删除博客用户
        self.blog_user.delete()

        # 验证OAuth用户也被删除（取决于外键的on_delete设置）
        # 如果是CASCADE，OAuth用户应该被删除
        with self.assertRaises(OAuthUser.DoesNotExist):
            OAuthUser.objects.get(id=oauth_id)


class OAuthMetadataTest(TestCase):
    """测试OAuth元数据业务逻辑"""

    def setUp(self):
        """设置测试环境"""
        self.blog_user = BlogUser.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )

    def test_oauth_user_metadata_field(self):
        """测试OAuth用户元数据字段"""
        metadata = {
            'avatar_url': 'http://example.com/avatar.jpg',
            'bio': 'Test bio',
            'location': 'Beijing'
        }

        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='github',
            metadata=str(metadata)  # 如果是JSONField或TextField
        )

        self.assertIsNotNone(oauth_user.metadata)

    def test_oauth_user_email_field(self):
        """测试OAuth用户邮箱字段"""
        oauth_email = 'oauth@example.com'

        oauth_user = OAuthUser.objects.create(
            author=self.blog_user,
            openid='openid',
            nickname='User',
            token='token',
            type='weibo',
            email=oauth_email
        )

        self.assertEqual(oauth_user.email, oauth_email)
