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
from elasticsearch_dsl.connections import connections
import time
from blog.models import Article, Category, Tag
from elasticsearch_dsl import Document, Date, Integer, Long, Keyword, Text, Object, Boolean

from django.conf import settings

ELASTICSEARCH_ENABLED = hasattr(settings, 'ELASTICSEARCH_DSL')

if ELASTICSEARCH_ENABLED:
    connections.create_connection(
        hosts=[settings.ELASTICSEARCH_DSL['default']['hosts']])


class ElapsedTimeDocument(Document):
    url = Text()
    time_taken = Long()
    log_datetime = Date()
    type = Text(analyzer='ik_max_word')
    useragent = Text()

    class Index:
        name = 'performance'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Meta:
        doc_type = 'ElapsedTime'


class ElaspedTimeDocumentManager():

    @staticmethod
    def create(url, time_taken, log_datetime, type, useragent):
        # if not hasattr(ElaspedTimeDocumentManager, 'mapping_created'):
        #     ElapsedTimeDocument.init()
        #     setattr(ElaspedTimeDocumentManager, 'mapping_created', True)
        doc = ElapsedTimeDocument(
            meta={
                'id': int(
                    round(
                        time.time() *
                        1000))},
            url=url,
            time_taken=time_taken,
            log_datetime=log_datetime,
            type=type,
            useragent=useragent)
        doc.save()


class ArticleDocument(Document):
    body = Text(analyzer='ik_max_word', search_analyzer='ik_smart')
    title = Text(analyzer='ik_max_word', search_analyzer='ik_smart')
    author = Object(properties={
        'nickname': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })
    category = Object(properties={
        'name': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })
    tags = Object(properties={
        'name': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })

    pub_time = Date()
    status = Text()
    comment_status = Text()
    type = Text()
    views = Integer()
    article_order = Integer()

    class Index:
        name = 'blog'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Meta:
        doc_type = 'Article'


class ArticleDocumentManager():

    def __init__(self):
        self.create_index()

    def create_index(self):
        ArticleDocument.init()

    def delete_index(self):
        from elasticsearch import Elasticsearch
        es = Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])
        es.indices.delete(index='blog', ignore=[400, 404])

    def convert_to_doc(self, articles):
        return [
            ArticleDocument(
                meta={
                    'id': article.id},
                body=article.body,
                title=article.title,
                author={
                    'nikename': article.author.username,
                    'id': article.author.id},
                category={
                    'name': article.category.name,
                    'id': article.category.id},
                tags=[
                    {
                        'name': t.name,
                        'id': t.id} for t in article.tags.all()],
                pub_time=article.pub_time,
                status=article.status,
                comment_status=article.comment_status,
                type=article.type,
                views=article.views,
                article_order=article.article_order) for article in articles]

    def rebuild(self, articles=None):
        ArticleDocument.init()
        articles = articles if articles else Article.objects.all()
        docs = self.convert_to_doc(articles)
        for doc in docs:
            doc.save()

    def update_docs(self, docs):
        for doc in docs:
            doc.save()
