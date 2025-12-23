"""
Django信号处理器

监听模型变更事件，触发Cloudflare缓存清除。
"""

import logging
from typing import List
from django.contrib.admin.models import LogEntry

logger = logging.getLogger(__name__)


class CloudflareCacheHandler:
    """Cloudflare缓存处理器"""

    def __init__(self, config: dict):
        """
        初始化处理器

        Args:
            config: 插件配置字典
        """
        self.config = config

        # 初始化Cloudflare API客户端
        from .api import CloudflareAPI
        self.cf_api = CloudflareAPI(
            zone_id=config['zone_id'],
            api_token=config['api_token']
        )

        logger.info("[CF Handler] Initialized with config")

    def on_model_save(self, sender, instance, created, update_fields, **kwargs):
        """
        Django post_save 信号处理器

        Args:
            sender: 发送信号的模型类
            instance: 保存的模型实例
            created: 是否为新建
            update_fields: 更新的字段集合
            **kwargs: 其他参数
        """
        # 忽略日志条目
        if isinstance(instance, LogEntry):
            return

        # 🚨 关键：忽略仅更新views字段的情况
        # 浏览量更新非常频繁，不应该清除缓存
        is_update_views = update_fields == {'views'}
        if is_update_views:
            logger.debug(f"[CF Handler] Skipping cache purge for views update: {instance}")
            return

        # 导入模型类（延迟导入避免循环依赖）
        from blog.models import Article
        from comments.models import Comment

        # 收集需要清除的URL
        urls_to_purge = []

        if isinstance(instance, Article):
            if self.config['purge_on_article_save']:
                urls_to_purge = self._collect_article_urls(instance, created)
                logger.info(f"[CF Handler] Article {'created' if created else 'updated'}: {instance.title}")

        elif isinstance(instance, Comment):
            if self.config['purge_on_comment_save'] and instance.is_enable:
                urls_to_purge = self._collect_comment_urls(instance, created)
                logger.info(f"[CF Handler] Comment {'created' if created else 'updated'} on article: {instance.article.title}")

        # 执行缓存清除
        if urls_to_purge:
            self._purge_cache_batch(urls_to_purge)

    def _collect_article_urls(self, article, is_new: bool) -> List[str]:
        """
        收集文章相关的URL

        Args:
            article: 文章实例
            is_new: 是否为新建文章

        Returns:
            需要清除的URL列表
        """
        from djangoblog.utils import get_current_site

        try:
            site = get_current_site()
            base_url = f"https://{site.domain}"

            urls = []

            # 1. 文章详情页（必须清除）
            article_url = base_url + article.get_absolute_url()
            urls.append(article_url)
            logger.debug(f"[CF Handler] Added article detail: {article_url}")

            # 2. 首页（如果配置启用）
            if self.config['purge_home_on_article']:
                home_url = base_url + '/'
                urls.append(home_url)
                logger.debug(f"[CF Handler] Added homepage: {home_url}")

            # 3. 相关页面（如果配置启用）
            if self.config['purge_related_pages']:
                # 分类页
                try:
                    category_url = base_url + article.category.get_absolute_url()
                    urls.append(category_url)
                    logger.debug(f"[CF Handler] Added category: {category_url}")
                except Exception as e:
                    logger.warning(f"[CF Handler] Failed to get category URL: {e}")

                # 标签页
                try:
                    for tag in article.tags.all():
                        tag_url = base_url + tag.get_absolute_url()
                        urls.append(tag_url)
                        logger.debug(f"[CF Handler] Added tag: {tag_url}")
                except Exception as e:
                    logger.warning(f"[CF Handler] Failed to get tag URLs: {e}")

                # RSS Feeds
                urls.append(base_url + '/rss/')
                urls.append(base_url + '/feed/')
                logger.debug(f"[CF Handler] Added RSS feeds")

            # 去重
            urls = list(dict.fromkeys(urls))

            logger.info(f"[CF Handler] Collected {len(urls)} URLs for article: {article.title}")
            return urls

        except Exception as e:
            logger.error(f"[CF Handler] Error collecting article URLs: {e}", exc_info=True)
            return []

    def _collect_comment_urls(self, comment, is_new: bool) -> List[str]:
        """
        收集评论相关的URL

        Args:
            comment: 评论实例
            is_new: 是否为新评论

        Returns:
            需要清除的URL列表
        """
        from djangoblog.utils import get_current_site

        try:
            site = get_current_site()
            base_url = f"https://{site.domain}"

            urls = []

            # 评论所在的文章页
            if comment.article:
                article_url = base_url + comment.article.get_absolute_url()
                urls.append(article_url)
                logger.debug(f"[CF Handler] Added article for comment: {article_url}")

                # 如果配置启用，也清除首页（显示最新评论的情况）
                if self.config.get('purge_home_on_comment', False):
                    urls.append(base_url + '/')

            logger.info(f"[CF Handler] Collected {len(urls)} URLs for comment")
            return urls

        except Exception as e:
            logger.error(f"[CF Handler] Error collecting comment URLs: {e}", exc_info=True)
            return []

    def _purge_cache_batch(self, urls: List[str]):
        """
        批量清除缓存

        Args:
            urls: 要清除的URL列表

        Note:
            - Cloudflare单次请求最多30个URL
            - 自动分批处理
        """
        if not urls:
            return

        max_urls = self.config['max_urls_per_request']

        try:
            # 分批处理
            for i in range(0, len(urls), max_urls):
                batch = urls[i:i + max_urls]

                logger.info(f"[CF Handler] Purging batch {i//max_urls + 1}: {len(batch)} URLs")

                result = self.cf_api.purge_urls(batch)

                if result.get('success'):
                    logger.info(f"[CF Handler] ✓ Successfully purged {len(batch)} URLs")
                else:
                    errors = result.get('errors', [])
                    error_messages = [err.get('message', str(err)) for err in errors]
                    logger.error(f"[CF Handler] ✗ Failed to purge batch: {error_messages}")

        except Exception as e:
            # 缓存清除失败不应影响主流程
            logger.error(f"[CF Handler] Exception during cache purge: {e}", exc_info=True)
            logger.warning("[CF Handler] Cache purge failed, but main operation completed successfully")

    def purge_all(self):
        """
        手动清除所有缓存

        Warning:
            此方法会清除整个Zone的所有缓存，请谨慎使用
        """
        logger.warning("[CF Handler] Manual purge all triggered")

        try:
            result = self.cf_api.purge_all()

            if result.get('success'):
                logger.info("[CF Handler] ✓ Successfully purged all cache")
                return True
            else:
                errors = result.get('errors', [])
                logger.error(f"[CF Handler] ✗ Failed to purge all: {errors}")
                return False

        except Exception as e:
            logger.error(f"[CF Handler] Exception during purge all: {e}", exc_info=True)
            return False
