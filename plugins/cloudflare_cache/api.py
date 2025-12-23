"""
Cloudflare API 封装

提供与Cloudflare API交互的功能，用于清除缓存。
"""

import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class CloudflareAPI:
    """Cloudflare API 客户端"""

    API_BASE = "https://api.cloudflare.com/client/v4"

    def __init__(self, zone_id: str, api_token: str):
        """
        初始化Cloudflare API客户端

        Args:
            zone_id: Cloudflare Zone ID
            api_token: Cloudflare API Token (需要 Zone.Cache Purge 权限)
        """
        self.zone_id = zone_id
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def purge_urls(self, urls: List[str]) -> Dict:
        """
        按URL清除缓存（精确清除）

        Args:
            urls: 要清除的URL列表（最多30个）

        Returns:
            API响应结果字典，包含 'success' 字段

        Note:
            - 单次请求最多清除30个URL
            - URL必须包含完整的协议和域名
            - 示例: https://example.com/article/123.html
        """
        if not urls:
            logger.warning("[CF API] No URLs to purge")
            return {'success': True, 'result': {'id': 'no-op'}}

        # Cloudflare限制单次最多30个URL
        if len(urls) > 30:
            logger.warning(f"[CF API] URLs count ({len(urls)}) exceeds limit (30), will be truncated")
            urls = urls[:30]

        endpoint = f"{self.API_BASE}/zones/{self.zone_id}/purge_cache"
        data = {'files': urls}

        try:
            logger.info(f"[CF API] Purging {len(urls)} URLs from cache")
            logger.debug(f"[CF API] URLs: {urls}")

            response = requests.post(
                endpoint,
                json=data,
                headers=self.headers,
                timeout=10
            )

            result = response.json()

            if result.get('success'):
                logger.info(f"[CF API] Successfully purged {len(urls)} URLs")
                logger.debug(f"[CF API] Response: {result}")
            else:
                errors = result.get('errors', [])
                logger.error(f"[CF API] Failed to purge cache: {errors}")

            return result

        except requests.Timeout:
            logger.error("[CF API] Request timeout (10s)")
            return {'success': False, 'errors': [{'message': 'Request timeout'}]}

        except requests.RequestException as e:
            logger.error(f"[CF API] Request failed: {e}", exc_info=True)
            return {'success': False, 'errors': [{'message': str(e)}]}

        except Exception as e:
            logger.error(f"[CF API] Unexpected error: {e}", exc_info=True)
            return {'success': False, 'errors': [{'message': f'Unexpected error: {e}'}]}

    def purge_all(self) -> Dict:
        """
        清除所有缓存（慎用！）

        Returns:
            API响应结果字典

        Warning:
            此操作会清除Zone下的所有缓存，影响范围大，请谨慎使用！
        """
        endpoint = f"{self.API_BASE}/zones/{self.zone_id}/purge_cache"
        data = {'purge_everything': True}

        try:
            logger.warning("[CF API] Purging ALL cache - this affects the entire zone!")

            response = requests.post(
                endpoint,
                json=data,
                headers=self.headers,
                timeout=10
            )

            result = response.json()

            if result.get('success'):
                logger.info("[CF API] Successfully purged all cache")
            else:
                errors = result.get('errors', [])
                logger.error(f"[CF API] Failed to purge all cache: {errors}")

            return result

        except requests.RequestException as e:
            logger.error(f"[CF API] Request failed: {e}", exc_info=True)
            return {'success': False, 'errors': [{'message': str(e)}]}

    def purge_by_tags(self, tags: List[str]) -> Dict:
        """
        按缓存标签清除（需要企业版）

        Args:
            tags: 缓存标签列表

        Returns:
            API响应结果字典

        Note:
            此功能仅在Cloudflare企业版中可用
        """
        endpoint = f"{self.API_BASE}/zones/{self.zone_id}/purge_cache"
        data = {'tags': tags}

        try:
            logger.info(f"[CF API] Purging cache by tags: {tags}")

            response = requests.post(
                endpoint,
                json=data,
                headers=self.headers,
                timeout=10
            )

            result = response.json()

            if result.get('success'):
                logger.info(f"[CF API] Successfully purged cache by tags")
            else:
                errors = result.get('errors', [])
                logger.error(f"[CF API] Failed to purge by tags: {errors}")

            return result

        except requests.RequestException as e:
            logger.error(f"[CF API] Request failed: {e}", exc_info=True)
            return {'success': False, 'errors': [{'message': str(e)}]}

    def validate_credentials(self) -> bool:
        """
        验证API凭证是否有效

        Returns:
            True 如果凭证有效，False 否则
        """
        endpoint = f"{self.API_BASE}/zones/{self.zone_id}"

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=5
            )

            result = response.json()

            if result.get('success'):
                logger.info("[CF API] Credentials validated successfully")
                return True
            else:
                logger.error(f"[CF API] Invalid credentials: {result.get('errors')}")
                return False

        except Exception as e:
            logger.error(f"[CF API] Failed to validate credentials: {e}")
            return False
