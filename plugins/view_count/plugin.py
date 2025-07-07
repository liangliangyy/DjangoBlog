from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks


class ViewCountPlugin(BasePlugin):
    PLUGIN_NAME = '文章浏览次数统计'
    PLUGIN_DESCRIPTION = '统计文章的浏览次数'
    PLUGIN_VERSION = '0.1.0'
    PLUGIN_AUTHOR = 'liangliangyy'

    def register_hooks(self):
        hooks.register('after_article_body_get', self.record_view)

    def record_view(self, article, *args, **kwargs):
        article.viewed()


plugin = ViewCountPlugin() 