from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks


class ArticleCopyrightPlugin(BasePlugin):
    PLUGIN_NAME = '文章结尾版权声明'
    PLUGIN_DESCRIPTION = '一个在文章正文末尾添加版权声明的插件。'
    PLUGIN_VERSION = '0.2.0'
    PLUGIN_AUTHOR = 'liangliangyy'

    # 2. 实现 register_hooks 方法，专门用于注册钩子
    def register_hooks(self):
        # 在这里将插件的方法注册到指定的钩子上
        hooks.register('the_content', self.add_copyright_to_content)

    def add_copyright_to_content(self, content, *args, **kwargs):
        """
        这个方法会被注册到 'the_content' 过滤器钩子上。
        它接收原始内容，并返回添加了版权信息的新内容。
        """
        article = kwargs.get('article')
        if not article:
            return content

        copyright_info = f"\n<hr><p>本文由 {article.author.nickname} 原创，转载请注明出处。</p>"
        return content + copyright_info


# 3. 实例化插件。
# 这会自动调用 BasePlugin.__init__，然后 BasePlugin.__init__ 会调用我们上面定义的 register_hooks 方法。
plugin = ArticleCopyrightPlugin()
