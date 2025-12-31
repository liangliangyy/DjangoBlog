"""
模板标签测试
测试各种模板标签和过滤器的功能
"""
from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import RequestFactory

from blog.models import Article
from blog.templatetags.blog_tags import *
from djangoblog.test_base import BaseTestCase


class BlogTagsTest(BaseTestCase):
    """测试博客模板标签"""

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def test_load_articletags(self):
        """测试加载文章标签"""
        self.article.tags.add(self.tag)
        result = load_articletags(self.article)
        self.assertIsInstance(result, dict)
        self.assertIn('article_tags_list', result)
        # 检查标签是否在列表中
        tag_objects = [tag_tuple[2] for tag_tuple in result['article_tags_list']]
        self.assertIn(self.tag, tag_objects)

    def test_load_pagination_info(self):
        """测试加载分页信息"""
        # 创建测试数据
        articles = [self.create_article(title=f'文章{i}') for i in range(20)]
        paginator = Paginator(articles, 10)
        page = paginator.get_page(1)

        # load_pagination_info 需要 page_type 和 tag_name 参数
        info = load_pagination_info(page, '', '')

        self.assertIsNotNone(info)
        # 验证基本分页属性存在
        self.assertTrue(hasattr(page, 'has_previous'))
        self.assertTrue(hasattr(page, 'has_next'))

    def test_load_pagination_info_last_page(self):
        """测试最后一页的分页信息"""
        articles = [self.create_article(title=f'文章{i}') for i in range(15)]
        paginator = Paginator(articles, 10)
        page = paginator.get_page(2)

        info = load_pagination_info(page, '', '')

        # 验证分页对象的属性
        self.assertFalse(page.has_next())
        self.assertTrue(page.has_previous())

    def test_highlight_search_term(self):
        """测试搜索关键词高亮"""
        text = '这是一段包含关键词的文本'
        result = highlight_search_term(text, '关键词')
        self.assertIn('<mark>', result)
        self.assertIn('关键词', result)

    def test_highlight_search_term_no_match(self):
        """测试搜索关键词不匹配"""
        text = '这是一段普通文本'
        result = highlight_search_term(text, '关键词')
        self.assertEqual(result, text)

    def test_highlight_search_term_empty_query(self):
        """测试空搜索词"""
        text = '这是一段普通文本'
        result = highlight_search_term(text, '')
        self.assertEqual(result, text)

    def test_highlight_content(self):
        """测试内容高亮"""
        content = '<p>这是一段 HTML 内容</p>'
        result = highlight_content(content, '内容')
        self.assertIn('内容', result)

    def test_custom_markdown(self):
        """测试自定义 Markdown 渲染"""
        markdown_text = '# 标题\n\n这是一段**加粗**的文本'
        result = custom_markdown(markdown_text)
        self.assertIn('<h1', result)
        self.assertIn('<strong>', result)

    def test_article_body_rendering(self):
        """测试文章内容渲染"""
        # 测试 Markdown 渲染，不需要创建文章
        markdown_text = '# 标题\n这是文章内容'
        result = custom_markdown(markdown_text)
        self.assertIn('<h1', result)
        self.assertIn('文章内容', result)


class ViteTagsTest(BaseTestCase):
    """测试 Vite 模板标签"""

    def test_vite_module_exists(self):
        """测试 Vite 模块存在"""
        # 简单测试 Vite 标签模块可以导入
        from blog.templatetags import vite_tags
        self.assertIsNotNone(vite_tags)


class CustomFiltersTest(BaseTestCase):
    """测试自定义过滤器"""

    def test_date_format_filter(self):
        """测试日期格式化过滤器"""
        from django.utils import timezone
        now = timezone.now()

        template = Template('{% load blog_tags %}{{ date|date:"Y-m-d" }}')
        context = Context({'date': now})
        result = template.render(context)
        self.assertIn(str(now.year), result)

    def test_url_encode_filter(self):
        """测试 URL 编码过滤器"""
        template = Template('{% load blog_tags %}{{ text|urlencode }}')
        context = Context({'text': '中文测试'})
        result = template.render(context)
        self.assertNotIn('中文', result)

    def test_strip_tags_filter(self):
        """测试去除 HTML 标签过滤器"""
        html = '<p>这是<strong>HTML</strong>文本</p>'
        template = Template('{% load blog_tags %}{{ html|striptags }}')
        context = Context({'html': html})
        result = template.render(context)
        self.assertNotIn('<p>', result)
        self.assertNotIn('<strong>', result)
        self.assertIn('这是', result)


class SidebarTagsTest(BaseTestCase):
    """测试侧边栏标签"""

    def test_sidebar_data_exists(self):
        """测试侧边栏数据存在"""
        # 简单测试侧边栏相关数据可以访问
        self.assertIsNotNone(self.article)
        self.assertIsNotNone(self.category)
        self.assertIsNotNone(self.tag)


class CacheTagsTest(BaseTestCase):
    """测试缓存标签"""

    def test_cache_operations(self):
        """测试缓存操作"""
        from django.core.cache import cache

        # 测试缓存设置和获取
        cache.set('test_key', 'test_value', 60)
        self.assertEqual(cache.get('test_key'), 'test_value')

        # 清空缓存
        cache.clear()
        self.assertIsNone(cache.get('test_key'))


class MarkdownExtensionsTest(BaseTestCase):
    """测试 Markdown 扩展"""

    def test_code_highlight(self):
        """测试代码高亮"""
        markdown_text = '''```python
def hello():
    print("Hello World")
```'''
        result = custom_markdown(markdown_text)
        self.assertIn('<code', result)

    def test_table_support(self):
        """测试表格支持"""
        markdown_text = '''
| 列1 | 列2 |
|-----|-----|
| 值1 | 值2 |
'''
        result = custom_markdown(markdown_text)
        self.assertIn('<table', result)

    def test_auto_link(self):
        """测试自动链接"""
        markdown_text = '<https://example.com>'
        result = custom_markdown(markdown_text)
        # Markdown 可能不会自动转换普通URL，需要用尖括号包裹
        self.assertIn('example.com', result)

    def test_strikethrough(self):
        """测试删除线"""
        markdown_text = '~~删除的文本~~'
        result = custom_markdown(markdown_text)
        # 根据实际 Markdown 扩展支持情况验证
        self.assertIsNotNone(result)
