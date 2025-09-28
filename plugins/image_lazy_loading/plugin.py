import re
import hashlib
from urllib.parse import urlparse
from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks
from djangoblog.plugin_manage.hook_constants import ARTICLE_CONTENT_HOOK_NAME


class ImageOptimizationPlugin(BasePlugin):
    PLUGIN_NAME = '图片性能优化插件'
    PLUGIN_DESCRIPTION = '自动为文章中的图片添加懒加载、异步解码等性能优化属性，显著提升页面加载速度。'
    PLUGIN_VERSION = '1.0.0'
    PLUGIN_AUTHOR = 'liangliangyy'

    def __init__(self):
        # 插件配置
        self.config = {
            'enable_lazy_loading': True,        # 启用懒加载
            'enable_async_decoding': True,      # 启用异步解码
            'add_loading_placeholder': True,    # 添加加载占位符
            'optimize_external_images': True,   # 优化外部图片
            'add_responsive_attributes': True,  # 添加响应式属性
            'skip_first_image': True,          # 跳过第一张图片（LCP优化）
        }
        super().__init__()

    def register_hooks(self):
        hooks.register(ARTICLE_CONTENT_HOOK_NAME, self.optimize_images)

    def optimize_images(self, content, *args, **kwargs):
        """
        优化文章中的图片标签
        """
        if not content:
            return content

        # 正则表达式匹配 img 标签
        img_pattern = re.compile(
            r'<img\s+([^>]*?)(?:\s*/)?>',
            re.IGNORECASE | re.DOTALL
        )

        image_count = 0
        
        def replace_img_tag(match):
            nonlocal image_count
            image_count += 1
            
            # 获取原始属性
            original_attrs = match.group(1)
            
            # 解析现有属性
            attrs = self._parse_img_attributes(original_attrs)
            
            # 应用优化
            optimized_attrs = self._apply_optimizations(attrs, image_count)
            
            # 重构 img 标签
            return self._build_img_tag(optimized_attrs)

        # 替换所有 img 标签
        optimized_content = img_pattern.sub(replace_img_tag, content)
        
        return optimized_content

    def _parse_img_attributes(self, attr_string):
        """
        解析 img 标签的属性
        """
        attrs = {}
        
        # 正则表达式匹配属性
        attr_pattern = re.compile(r'(\w+)=(["\'])(.*?)\2')
        
        for match in attr_pattern.finditer(attr_string):
            attr_name = match.group(1).lower()
            attr_value = match.group(3)
            attrs[attr_name] = attr_value
            
        return attrs

    def _apply_optimizations(self, attrs, image_index):
        """
        应用各种图片优化
        """
        # 1. 懒加载优化（跳过第一张图片以优化LCP）
        if self.config['enable_lazy_loading']:
            if not (self.config['skip_first_image'] and image_index == 1):
                if 'loading' not in attrs:
                    attrs['loading'] = 'lazy'

        # 2. 异步解码
        if self.config['enable_async_decoding']:
            if 'decoding' not in attrs:
                attrs['decoding'] = 'async'

        # 3. 添加样式优化
        current_style = attrs.get('style', '')
        
        # 确保图片不会超出容器
        if 'max-width' not in current_style:
            if current_style and not current_style.endswith(';'):
                current_style += ';'
            current_style += 'max-width:100%;height:auto;'
            attrs['style'] = current_style

        # 4. 添加 alt 属性（SEO和可访问性）
        if 'alt' not in attrs:
            # 尝试从图片URL生成有意义的alt文本
            src = attrs.get('src', '')
            if src:
                # 从文件名生成alt文本
                filename = src.split('/')[-1].split('.')[0]
                # 移除常见的无意义字符
                clean_name = re.sub(r'[0-9a-f]{8,}', '', filename)  # 移除长hash
                clean_name = re.sub(r'[_-]+', ' ', clean_name).strip()
                attrs['alt'] = clean_name if clean_name else '文章图片'
            else:
                attrs['alt'] = '文章图片'

        # 5. 外部图片优化
        if self.config['optimize_external_images'] and 'src' in attrs:
            src = attrs['src']
            parsed_url = urlparse(src)
            
            # 如果是外部图片，添加 referrerpolicy
            if parsed_url.netloc and parsed_url.netloc != self._get_current_domain():
                attrs['referrerpolicy'] = 'no-referrer-when-downgrade'
                # 为外部图片添加crossorigin属性以支持性能监控
                if 'crossorigin' not in attrs:
                    attrs['crossorigin'] = 'anonymous'

        # 6. 响应式图片属性（如果配置启用）
        if self.config['add_responsive_attributes']:
            # 添加 sizes 属性（如果没有的话）
            if 'sizes' not in attrs and 'srcset' not in attrs:
                attrs['sizes'] = '(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'

        # 7. 添加图片唯一标识符用于性能追踪
        if 'data-img-id' not in attrs and 'src' in attrs:
            img_hash = hashlib.md5(attrs['src'].encode()).hexdigest()[:8]
            attrs['data-img-id'] = f'img-{img_hash}'

        # 8. 为第一张图片添加高优先级提示（LCP优化）
        if image_index == 1 and self.config['skip_first_image']:
            attrs['fetchpriority'] = 'high'
            # 移除懒加载以确保快速加载
            if 'loading' in attrs:
                del attrs['loading']

        return attrs

    def _build_img_tag(self, attrs):
        """
        重新构建 img 标签
        """
        attr_strings = []
        
        # 确保 src 属性在最前面
        if 'src' in attrs:
            attr_strings.append(f'src="{attrs["src"]}"')
            
        # 添加其他属性
        for key, value in attrs.items():
            if key != 'src':  # src 已经添加过了
                attr_strings.append(f'{key}="{value}"')
        
        return f'<img {" ".join(attr_strings)}>'

    def _get_current_domain(self):
        """
        获取当前网站域名
        """
        try:
            from djangoblog.utils import get_current_site
            return get_current_site().domain
        except:
            return ''


# 实例化插件
plugin = ImageOptimizationPlugin()
