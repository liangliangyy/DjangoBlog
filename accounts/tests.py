from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
import datetime
from accounts.models import BlogUser


# Create your tests here.

class AccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_account(self):
        site = Site.objects.get_current().domain
        user = BlogUser.objects.create_superuser(email="liangliangyy1@gmail.com",
                                                 username="liangliangyy1", password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

        category = Category()
        category.name = "categoryaaa"
        category.created_time = datetime.datetime.now()
        category.last_mod_time = datetime.datetime.now()
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
