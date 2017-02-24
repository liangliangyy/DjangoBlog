from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
import datetime


# Create your tests here.

class ArticleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_article(self):
        from accounts.models import BlogUser
        site = Site.objects.get_current().domain
        user = BlogUser()
        user.email = "liangliangyy@gmail.com"
        user.username = "liangliangyy"
        user.password = "liangliangyy"
        user.set_password("liangliangyy")
        user.save()
        response = self.client.get(user.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        category = Category()
        category.name = "category"
        category.created_time = datetime.datetime.now()
        category.last_mod_time = datetime.datetime.now()
        category.save()

        response = self.client.get(category.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        article = Article()
        article.title = "nicetitle"
        article.body = "nicecontent"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'
        article.save()
        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)