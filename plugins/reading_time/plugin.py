import math
import re
from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks
from djangoblog.plugin_manage.hook_constants import ARTICLE_CONTENT_HOOK_NAME


class ReadingTimePlugin(BasePlugin):
    PLUGIN_NAME = '阅读时间预测'
    PLUGIN_DESCRIPTION = '估算文章阅读时间并显示在文章开头。'
    PLUGIN_VERSION = '0.1.0'
    PLUGIN_AUTHOR = 'liangliangyy'

    def register_hooks(self):
        hooks.register(ARTICLE_CONTENT_HOOK_NAME, self.add_reading_time)

    def add_reading_time(self, content, *args, **kwargs):
        """
        计算阅读时间并添加到内容开头。
        只在文章详情页显示，首页（文章列表页）不显示。
        """
        # 检查是否为摘要模式（首页/文章列表页）
        # 通过kwargs中的is_summary参数判断
        is_summary = kwargs.get('is_summary', False)
        if is_summary:
            # 如果是摘要模式（首页），直接返回原内容，不添加阅读时间
            return content
        
        # 移除HTML标签和空白字符，以获得纯文本
        clean_content = re.sub(r'<[^>]*>', '', content)
        clean_content = clean_content.strip()
        
        # 中文和英文单词混合计数的一个简单方法
        # 匹配中文字符或连续的非中文字符(视为单词)
        words = re.findall(r'[\u4e00-\u9fa5]|\w+', clean_content)
        word_count = len(words)
        
        # 按平均每分钟200字的速度计算
        reading_speed = 200
        reading_minutes = math.ceil(word_count / reading_speed)

        # 如果阅读时间少于1分钟，则显示为1分钟
        if reading_minutes < 1:
            reading_minutes = 1
            
        reading_time_html = f'<p style="color: #888;"><em>预计阅读时间：{reading_minutes} 分钟</em></p>'
        
        return reading_time_html + content


plugin = ReadingTimePlugin() 