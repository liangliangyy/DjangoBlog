#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: documents.py
@time: 2019-04-05 13:05
"""

from django_elasticsearch_dsl import DocType, Index, fields
from blog.models import Article, Category, Tag
from accounts.models import BlogUser

blog = Index('blog')
blog.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@blog.doc_type
class ArticleDocument(DocType):
    body = fields.TextField(attr='body_to_string', analyzer='ik_max_word')
    title = fields.TextField(analyzer='ik_max_word')
    author = fields.ObjectField(properties={
        'nickname': fields.TextField(analyzer='ik_max_word'),
        'id': fields.IntegerField()
    })
    category = fields.ObjectField(properties={
        'name': fields.TextField(analyzer='ik_max_word'),
        'id': fields.IntegerField()
    })
    tags = fields.ObjectField(properties={
        'name': fields.TextField(analyzer='ik_max_word'),
        'id': fields.IntegerField()
    })

    # def get_instances_from_related(self, related_instance):
    #     if isinstance(related_instance, BlogUser):
    #         return related_instance
    #     elif isinstance(related_instance, Category):
    #         pass

    class Meta:
        model = Article
        fields = [
            'pub_time',
            'status',
            'comment_status',
            'type',
            'views',
            'article_order',

        ]
        # related_models = [Category, Tag, BlogUser]
        doc_type = 'Article'
        auto_refresh = False
        ignore_signals = True

