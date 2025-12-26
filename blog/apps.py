from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        """应用启动时的初始化"""
        # 检查并创建搜索索引（如果需要）
        self.check_search_index()

    def check_search_index(self):
        """检查搜索索引是否存在，不存在则创建空索引"""
        from django.conf import settings

        # 1. 检查Elasticsearch索引
        if hasattr(settings, 'ELASTICSEARCH_DSL'):
            try:
                from blog.documents import ELASTICSEARCH_ENABLED, ArticleDocumentManager
                if ELASTICSEARCH_ENABLED:
                    from elasticsearch import Elasticsearch
                    es_config = settings.ELASTICSEARCH_DSL['default']
                    es = Elasticsearch(hosts=[es_config['hosts']], verify_certs=False)

                    # 检查blog索引是否存在
                    if not es.indices.exists(index='blog'):
                        logger.info("Elasticsearch blog index not found, creating empty index...")
                        manager = ArticleDocumentManager()
                        logger.info("Elasticsearch blog index created successfully")
                    else:
                        logger.debug("Elasticsearch blog index already exists")
            except Exception as e:
                logger.warning(f"Failed to check/create Elasticsearch index: {e}")

        # 2. 检查Whoosh索引
        haystack_engine = settings.HAYSTACK_CONNECTIONS.get('default', {}).get('ENGINE', '')
        if 'whoosh' in haystack_engine.lower():
            try:
                import os
                whoosh_path = settings.HAYSTACK_CONNECTIONS['default'].get('PATH')
                if whoosh_path and not os.path.exists(whoosh_path):
                    logger.info(f"Whoosh index directory not found at {whoosh_path}, will be created on first search")
                    # Whoosh会在第一次搜索时自动创建，这里只记录日志
                elif whoosh_path and os.path.exists(whoosh_path):
                    # 检查是否有索引文件
                    index_files = [f for f in os.listdir(whoosh_path) if f.endswith('.seg') or f == '_MAIN_WRITELOCK']
                    if not index_files:
                        logger.info("Whoosh index directory exists but empty, will be initialized on first search")
                    else:
                        logger.debug("Whoosh index already exists")
            except Exception as e:
                logger.warning(f"Failed to check Whoosh index: {e}")
