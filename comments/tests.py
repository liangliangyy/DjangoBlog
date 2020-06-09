from django.test import Client, RequestFactory, TestCase
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from DjangoBlog.utils import get_current_site
from django.urls import reverse
from django.utils import timezone
from accounts.models import BlogUser
from comments.templatetags.comments_tags import *
from DjangoBlog.utils import get_max_articleid_commentid


# Create your tests here.

class CommentsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_comment(self):
        site = get_current_site().domain
        user = BlogUser.objects.create_superuser(
            email="liangliangyy1@gmail.com",
            username="liangliangyy1",
            password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')

        category = Category()
        category.name = "categoryccc"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.title = "nicetitleccc"
        article.body = "nicecontentccc"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'
        article.save()

        commenturl = reverse(
            'comments:postcomment', kwargs={
                'article_id': article.id})

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
        parent_comment_id = article.comment_list()[0].id

        response = self.client.post(commenturl,
                                    {
                                        'body': '''
                                        # Title1

        ```python
        import os
        ```

        [url](https://www.lylinux.net/)

        [ddd](http://www.baidu.com)


        ''',
                                        'email': user.email,
                                        'name': user.username,
                                        'parent_comment_id': parent_comment_id
                                    })

        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(pk=article.pk)
        self.assertEqual(len(article.comment_list()), 2)
        comment = Comment.objects.get(id=parent_comment_id)
        tree = parse_commenttree(article.comment_list(), comment)
        self.assertEqual(len(tree), 1)
        data = show_comment_item(comment, True)
        self.assertIsNotNone(data)
        s = get_max_articleid_commentid()
        self.assertIsNotNone(s)
