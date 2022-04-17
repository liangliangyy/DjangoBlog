from django.conf import settings
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from djangoblog.utils import *
from accounts.models import BlogUser
from blog.models import Article, Category
from . import utils


# Create your tests here.

class AccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.blog_user = BlogUser.objects.create_user(
            username="test",
            email="admin@admin.com",
            password="12345678"
        )
        self.new_test = "xxx123--="

    def test_validate_account(self):
        site = get_current_site().domain
        user = BlogUser.objects.create_superuser(
            email="liangliangyy1@gmail.com",
            username="liangliangyy1",
            password="qwer!@#$ggg")
        testuser = BlogUser.objects.get(username='liangliangyy1')

        loginresult = self.client.login(
            username='liangliangyy1',
            password='qwer!@#$ggg')
        self.assertEqual(loginresult, True)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

        category = Category()
        category.name = "categoryaaa"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.title = "nicetitleaaa"
        article.body = "nicecontentaaa"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'
        article.save()

        response = self.client.get(article.get_admin_url())
        self.assertEqual(response.status_code, 200)

    def test_validate_register(self):
        self.assertEquals(
            0, len(
                BlogUser.objects.filter(
                    email='user123@user.com')))
        response = self.client.post(reverse('account:register'), {
            'username': 'user1233',
            'email': 'user123@user.com',
            'password1': 'password123!q@wE#R$T',
            'password2': 'password123!q@wE#R$T',
        })
        self.assertEquals(
            1, len(
                BlogUser.objects.filter(
                    email='user123@user.com')))
        user = BlogUser.objects.filter(email='user123@user.com')[0]
        sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
        path = reverse('accounts:result')
        url = '{path}?type=validation&id={id}&sign={sign}'.format(
            path=path, id=user.id, sign=sign)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user1233', password='password123!q@wE#R$T')
        user = BlogUser.objects.filter(email='user123@user.com')[0]
        user.is_superuser = True
        user.is_staff = True
        user.save()
        delete_sidebar_cache()
        category = Category()
        category.name = "categoryaaa"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.category = category
        article.title = "nicetitle333"
        article.body = "nicecontentttt"
        article.author = user

        article.type = 'a'
        article.status = 'p'
        article.save()

        response = self.client.get(article.get_admin_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('account:logout'))
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.get(article.get_admin_url())
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.post(reverse('account:login'), {
            'username': 'user1233',
            'password': 'password123'
        })
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.get(article.get_admin_url())
        self.assertIn(response.status_code, [301, 302, 200])

    def test_verify_email_code(self):
        to_email = "admin@admin.com"
        code = generate_code()
        utils.set_code(to_email, code)
        utils.send_verify_email(to_email, code)

        err = utils.verify("admin@admin.com", code)
        self.assertEqual(err, None)

        err = utils.verify("admin@123.com", code)
        self.assertEqual(type(err), str)

    def test_forget_password_email_code_success(self):
        resp = self.client.post(
            path=reverse("account:forget_password_code"),
            data=dict(email="admin@admin.com")
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode("utf-8"), "ok")

    def test_forget_password_email_code_fail(self):
        resp = self.client.post(
            path=reverse("account:forget_password_code"),
            data=dict()
        )
        self.assertEqual(resp.content.decode("utf-8"), "错误的邮箱")

        resp = self.client.post(
            path=reverse("account:forget_password_code"),
            data=dict(email="admin@com")
        )
        self.assertEqual(resp.content.decode("utf-8"), "错误的邮箱")

    def test_forget_password_email_success(self):
        code = generate_code()
        utils.set_code(self.blog_user.email, code)
        data = dict(
            new_password1=self.new_test,
            new_password2=self.new_test,
            email=self.blog_user.email,
            code=code,
        )
        resp = self.client.post(
            path=reverse("account:forget_password"),
            data=data
        )
        self.assertEqual(resp.status_code, 302)

        # 验证用户密码是否修改成功
        blog_user = BlogUser.objects.filter(
            email=self.blog_user.email,
        ).first()  # type: BlogUser
        self.assertNotEqual(blog_user, None)
        self.assertEqual(blog_user.check_password(data["new_password1"]), True)

    def test_forget_password_email_not_user(self):
        data = dict(
            new_password1=self.new_test,
            new_password2=self.new_test,
            email="123@123.com",
            code="123456",
        )
        resp = self.client.post(
            path=reverse("account:forget_password"),
            data=data
        )

        self.assertEqual(resp.status_code, 200)
        self.assertFormError(
            response=resp,
            form="form",
            field="email",
            errors="未找到邮箱对应的用户"
        )

    def test_forget_password_email_code_error(self):
        code = generate_code()
        utils.set_code(self.blog_user.email, code)
        data = dict(
            new_password1=self.new_test,
            new_password2=self.new_test,
            email=self.blog_user.email,
            code="111111",
        )
        resp = self.client.post(
            path=reverse("account:forget_password"),
            data=data
        )

        self.assertEqual(resp.status_code, 200)
        self.assertFormError(
            response=resp,
            form="form",
            field="code",
            errors="验证码错误"
        )
