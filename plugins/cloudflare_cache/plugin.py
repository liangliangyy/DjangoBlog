"""
Cloudflare 缓存管理插件

自动清除Cloudflare CDN缓存，确保内容更新后用户能看到最新内容。

功能特性：
- 文章发布/修改时自动清除相关页面缓存
- 评论发布时清除文章页面缓存
- 智能过滤浏览量更新，避免频繁清除缓存
- 支持批量清除，自动处理Cloudflare的30个URL限制
- 完整的错误处理，缓存清除失败不影响主流程
- 灵活的配置选项，可按需启用/禁用功能

作者: DjangoBlog
版本: 1.0.0
"""

import os
import logging
from django.conf import settings
from django.db.models.signals import post_save

from djangoblog.plugin_manage.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class CloudflareCachePlugin(BasePlugin):
    """Cloudflare 缓存管理插件"""

    # ==================== 插件元数据 ====================
    PLUGIN_NAME = 'Cloudflare 缓存管理'
    PLUGIN_DESCRIPTION = '自动清除Cloudflare缓存，在文章、评论更新时保持内容同步'
    PLUGIN_VERSION = '1.0.0'
    PLUGIN_AUTHOR = 'DjangoBlog'

    # ==================== 位置配置 ====================
    # 此插件不需要在页面上显示任何内容，只在后台工作
    SUPPORTED_POSITIONS = []

    # ==================== 插件配置 ====================
    CONFIG = {
        # === 基础配置 ===
        'enabled': True,  # 插件总开关

        # Cloudflare 凭证（从环境变量或Django settings读取）
        'zone_id': os.environ.get('CLOUDFLARE_ZONE_ID', ''),
        'api_token': os.environ.get('CLOUDFLARE_API_TOKEN', ''),

        # === 清除策略 ===
        'purge_on_article_save': True,   # 文章保存时清除缓存
        'purge_on_comment_save': True,   # 评论保存时清除缓存

        # === 清除范围 ===
        'purge_home_on_article': True,    # 文章更新时是否清除首页
        'purge_related_pages': True,      # 是否清除分类页、标签页、RSS等相关页面
        'purge_home_on_comment': True,   # 评论更新时是否清除首页（如果首页显示最新评论则开启）

        # === API 配置 ===
        'max_urls_per_request': 30,  # 单次请求最多清除的URL数（Cloudflare限制）
        'request_timeout': 10,        # API请求超时时间（秒）

        # === 建议配置 ===
        'recommended_cache_ttl': 7200,  # 建议的缓存TTL（2小时）
    }

    def init_plugin(self):
        """插件初始化"""
        logger.info(f"Initializing {self.PLUGIN_NAME} v{self.PLUGIN_VERSION}")

        # 从Django settings读取配置（如果存在）
        if hasattr(settings, 'CLOUDFLARE_CONFIG'):
            cf_config = settings.CLOUDFLARE_CONFIG
            self.CONFIG['zone_id'] = cf_config.get('zone_id', self.CONFIG['zone_id'])
            self.CONFIG['api_token'] = cf_config.get('api_token', self.CONFIG['api_token'])
            logger.info("[CF Plugin] Loaded config from Django settings")

        # 验证配置
        if not self._validate_config():
            self.CONFIG['enabled'] = False
            logger.warning("[CF Plugin] Plugin disabled due to invalid configuration")
            return

        logger.info("[CF Plugin] Configuration validated successfully")

        # 测试API连接（可选）
        if self.CONFIG.get('test_on_init', False):
            self._test_api_connection()

    def _validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            True 如果配置有效，False 否则
        """
        zone_id = self.CONFIG.get('zone_id', '').strip()
        api_token = self.CONFIG.get('api_token', '').strip()

        if not zone_id:
            logger.error("[CF Plugin] CLOUDFLARE_ZONE_ID not configured")
            logger.info("[CF Plugin] Please set environment variable: CLOUDFLARE_ZONE_ID")
            return False

        if not api_token:
            logger.error("[CF Plugin] CLOUDFLARE_API_TOKEN not configured")
            logger.info("[CF Plugin] Please set environment variable: CLOUDFLARE_API_TOKEN")
            return False

        # 基本格式验证
        if len(zone_id) != 32:
            logger.warning(f"[CF Plugin] Zone ID format may be invalid (length: {len(zone_id)})")

        if len(api_token) < 20:
            logger.warning(f"[CF Plugin] API Token format may be invalid (length: {len(api_token)})")

        return True

    def _test_api_connection(self):
        """测试Cloudflare API连接"""
        try:
            from .api import CloudflareAPI

            cf_api = CloudflareAPI(
                zone_id=self.CONFIG['zone_id'],
                api_token=self.CONFIG['api_token']
            )

            if cf_api.validate_credentials():
                logger.info("[CF Plugin] ✓ API connection test successful")
            else:
                logger.error("[CF Plugin] ✗ API connection test failed")
                logger.warning("[CF Plugin] Plugin will continue, but cache purging may not work")

        except Exception as e:
            logger.error(f"[CF Plugin] Error testing API connection: {e}")

    def register_hooks(self):
        """注册Django信号钩子"""
        if not self.CONFIG['enabled']:
            logger.info("[CF Plugin] Plugin is disabled, skipping hook registration")
            return

        try:
            # 导入模型类
            from blog.models import Article
            from comments.models import Comment
            from .handlers import CloudflareCacheHandler

            # 初始化处理器
            self.handler = CloudflareCacheHandler(self.CONFIG)

            # 注册Article模型的post_save信号
            if self.CONFIG['purge_on_article_save']:
                post_save.connect(
                    self.handler.on_model_save,
                    sender=Article,
                    dispatch_uid='cloudflare_cache_article_save'
                )
                logger.info("[CF Plugin] Registered hook: Article.post_save")

            # 注册Comment模型的post_save信号
            if self.CONFIG['purge_on_comment_save']:
                post_save.connect(
                    self.handler.on_model_save,
                    sender=Comment,
                    dispatch_uid='cloudflare_cache_comment_save'
                )
                logger.info("[CF Plugin] Registered hook: Comment.post_save")

            logger.info("[CF Plugin] All hooks registered successfully")

        except ImportError as e:
            logger.error(f"[CF Plugin] Failed to import dependencies: {e}")
            self.CONFIG['enabled'] = False

        except Exception as e:
            logger.error(f"[CF Plugin] Error registering hooks: {e}", exc_info=True)
            self.CONFIG['enabled'] = False

    # ==================== 管理命令接口 ====================

    def purge_all_cache(self):
        """
        手动清除所有缓存

        Returns:
            bool: 是否成功

        Warning:
            此操作会清除整个Zone的所有缓存！
        """
        if not self.CONFIG['enabled']:
            logger.error("[CF Plugin] Plugin is not enabled")
            return False

        if hasattr(self, 'handler'):
            return self.handler.purge_all()
        else:
            logger.error("[CF Plugin] Handler not initialized")
            return False

    def get_plugin_status(self) -> dict:
        """
        获取插件状态

        Returns:
            包含插件状态信息的字典
        """
        return {
            'name': self.PLUGIN_NAME,
            'version': self.PLUGIN_VERSION,
            'enabled': self.CONFIG['enabled'],
            'zone_id_configured': bool(self.CONFIG.get('zone_id')),
            'api_token_configured': bool(self.CONFIG.get('api_token')),
            'purge_on_article': self.CONFIG['purge_on_article_save'],
            'purge_on_comment': self.CONFIG['purge_on_comment_save'],
        }


# ==================== 插件实例（必需）====================
plugin = CloudflareCachePlugin()
