import re
from urllib.parse import urlparse
from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks
from djangoblog.plugin_manage.hook_constants import ARTICLE_CONTENT_HOOK_NAME


class ExternalLinksPlugin(BasePlugin):
    PLUGIN_NAME = '外部链接处理器'
    PLUGIN_DESCRIPTION = '自动为文章中的外部链接添加 target="_blank" 和 rel="noopener noreferrer" 属性。'
    PLUGIN_VERSION = '0.1.0'
    PLUGIN_AUTHOR = 'liangliangyy'

    def register_hooks(self):
        hooks.register(ARTICLE_CONTENT_HOOK_NAME, self.process_external_links)

    def process_external_links(self, content, *args, **kwargs):
        from djangoblog.utils import get_current_site
        site_domain = get_current_site().domain

        # 正则表达式查找所有 <a> 标签
        link_pattern = re.compile(r'(<a\s+(?:[^>]*?\s+)?href=")([^"]*)(".*?/a>)', re.IGNORECASE)

        def replacer(match):
            # match.group(1) 是 <a ... href="
            # match.group(2) 是链接 URL
            # match.group(3) 是 ">...</a>
            href = match.group(2)

            # 如果链接已经有 target 属性，则不处理
            if 'target=' in match.group(0).lower():
                return match.group(0)

            # 解析链接
            parsed_url = urlparse(href)

            # 如果链接是外部的 (有域名且域名不等于当前网站域名)
            if parsed_url.netloc and parsed_url.netloc != site_domain:
                # 添加 target 和 rel 属性
                return f'{match.group(1)}{href}" target="_blank" rel="noopener noreferrer"{match.group(3)}'

            # 否则返回原样
            return match.group(0)

        return link_pattern.sub(replacer, content)


plugin = ExternalLinksPlugin()
