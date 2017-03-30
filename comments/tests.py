from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import datetime
from accounts.models import BlogUser


# Create your tests here.

class CommentsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_comment(self):
        site = Site.objects.get_current().domain
        user = BlogUser.objects.create_superuser(email="liangliangyy1@gmail.com",
                                                 username="liangliangyy1", password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')

        category = Category()
        category.name = "categoryccc"
        category.created_time = datetime.datetime.now()
        category.last_mod_time = datetime.datetime.now()
        category.save()

        article = Article()
        article.title = "nicetitleccc"
        article.body = "nicecontentccc"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'
        article.save()

        commenturl = reverse('comments:postcomment', kwargs={'article_id': article.id})

        response = self.client.post(commenturl,
                                    {
                                        'body': '123ffffffffff'
                                    })

        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(pk=article.pk)
        self.assertEqual(len(article.comment_list()), 0)

        response = self.client.post(commenturl,
                                    {
                                        'body': '123ffffffffff',
                                        'email': user.email,
                                        'name': user.username
                                    })

        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(pk=article.pk)
        self.assertEqual(len(article.comment_list()), 1)
