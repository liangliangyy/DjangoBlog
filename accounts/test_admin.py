"""
Accounts Admin 测试
测试用户管理后台的各项功能
"""
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse

from accounts.admin import BlogUserAdmin
from accounts.models import BlogUser
from djangoblog.test_base import BaseTestCase, AdminTestMixin


class BlogUserAdminTest(BaseTestCase, AdminTestMixin):
    """测试 BlogUser Admin"""

    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.blog_user_admin = BlogUserAdmin(BlogUser, self.site)

    def test_admin_list_display(self):
        """测试列表显示字段"""
        self.login_admin()
        response = self.assert_admin_accessible(BlogUser)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_admin_search(self):
        """测试搜索功能"""
        self.login_admin()
        url = self.get_admin_url(BlogUser)
        response = self.client.get(url, {'q': self.user.username})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_admin_filter_by_is_staff(self):
        """测试按员工状态过滤"""
        staff_user = self.create_staff_user()
        self.login_admin()
        url = self.get_admin_url(BlogUser)
        response = self.client.get(url, {'is_staff__exact': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, staff_user.username)

    def test_admin_change_user(self):
        """测试修改用户"""
        self.login_admin()
        url = self.get_admin_change_url(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 修改用户信息
        response = self.client.post(url, {
            'username': self.user.username,
            'email': 'newemail@test.com',
            'date_joined_0': self.user.date_joined.strftime('%Y-%m-%d'),
            'date_joined_1': self.user.date_joined.strftime('%H:%M:%S'),
        })
        self.user.refresh_from_db()

    def test_admin_requires_login(self):
        """测试需要登录才能访问"""
        self.client.logout()
        self.assert_admin_forbidden_for_user(BlogUser)

    def test_admin_forbidden_for_normal_user(self):
        """测试普通用户无法访问"""
        self.login_user()
        self.assert_admin_forbidden_for_user(BlogUser)

    def test_get_list_filter(self):
        """测试获取列表过滤器"""
        request = self.factory.get('/')
        request.user = self.admin_user
        filters = self.blog_user_admin.get_list_filter(request)
        self.assertIn('is_staff', filters)
        self.assertIn('is_superuser', filters)

    def test_get_readonly_fields_for_superuser(self):
        """测试超级管理员看到的只读字段"""
        request = self.factory.get('/')
        request.user = self.admin_user
        readonly_fields = self.blog_user_admin.get_readonly_fields(request, self.user)
        self.assertIsInstance(readonly_fields, (list, tuple))

    def test_get_readonly_fields_for_staff(self):
        """测试员工用户看到的只读字段"""
        staff = self.create_staff_user()
        request = self.factory.get('/')
        request.user = staff
        readonly_fields = self.blog_user_admin.get_readonly_fields(request, self.user)
        # 员工用户应该看到更多只读字段
        self.assertIsInstance(readonly_fields, (list, tuple))
