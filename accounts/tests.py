from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from DjangoBlog.utils import delete_view_cache, delete_sidebar_cache
from accounts.models import BlogUser
from django.urls import reverse
from DjangoBlog.utils import *
from django.conf import settings
from django.utils import timezone


# Create your tests here.

class AccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

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
        sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
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
        delete_sidebar_cache(user.username)
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
