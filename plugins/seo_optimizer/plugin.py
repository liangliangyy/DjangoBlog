import json
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords
from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks
from blog.models import Article, Category, Tag
from djangoblog.utils import get_blog_setting


class SeoOptimizerPlugin(BasePlugin):
    PLUGIN_NAME = 'SEO 优化器'
    PLUGIN_DESCRIPTION = '为文章、页面等提供 SEO 优化，动态生成 meta 标签和 JSON-LD 结构化数据。'
    PLUGIN_VERSION = '0.2.0'
    PLUGIN_AUTHOR = 'Gemini'

    def register_hooks(self):
        hooks.register('head_meta', self.dispatch_seo_generation)

    def _get_article_seo_data(self, context, request, blog_setting):
        article = context.get('article')
        if not isinstance(article, Article):
            return None

        description = strip_tags(article.body)[:150]
        keywords = ",".join([tag.name for tag in article.tags.all()]) or blog_setting.site_keywords
        
        meta_tags = f'''
        <meta property="og:type" content="article"/>
        <meta property="og:title" content="{article.title}"/>
        <meta property="og:description" content="{description}"/>
        <meta property="og:url" content="{request.build_absolute_uri()}"/>
        <meta property="article:published_time" content="{article.pub_time.isoformat()}"/>
        <meta property="article:modified_time" content="{article.last_modify_time.isoformat()}"/>
        <meta property="article:author" content="{article.author.username}"/>
        <meta property="article:section" content="{article.category.name}"/>
        '''
        for tag in article.tags.all():
            meta_tags += f'<meta property="article:tag" content="{tag.name}"/>'
        meta_tags += f'<meta property="og:site_name" content="{blog_setting.site_name}"/>'

        structured_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "mainEntityOfPage": {"@type": "WebPage", "@id": request.build_absolute_uri()},
            "headline": article.title,
            "description": description,
            "image": request.build_absolute_uri(article.get_first_image_url()),
            "datePublished": article.pub_time.isoformat(),
            "dateModified": article.last_modify_time.isoformat(),
            "author": {"@type": "Person", "name": article.author.username},
            "publisher": {"@type": "Organization", "name": blog_setting.site_name}
        }
        if not structured_data.get("image"):
            del structured_data["image"]

        return {
            "title": f"{article.title} | {blog_setting.site_name}",
            "description": description,
            "keywords": keywords,
            "meta_tags": meta_tags,
            "json_ld": structured_data
        }

    def _get_category_seo_data(self, context, request, blog_setting):
        category_name = context.get('tag_name')
        if not category_name:
            return None
        
        category = Category.objects.filter(name=category_name).first()
        if not category:
            return None

        title = f"{category.name} | {blog_setting.site_name}"
        description = strip_tags(category.name) or blog_setting.site_description
        keywords = category.name

        # BreadcrumbList structured data for category page
        breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "首页", "item": request.build_absolute_uri('/')}]
        breadcrumb_items.append({"@type": "ListItem", "position": 2, "name": category.name, "item": request.build_absolute_uri()})
        
        structured_data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }

        return {
            "title": title,
            "description": description,
            "keywords": keywords,
            "meta_tags": "",
            "json_ld": structured_data
        }

    def _get_default_seo_data(self, context, request, blog_setting):
        # Homepage and other default pages
        structured_data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "url": request.build_absolute_uri('/'),
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{request.build_absolute_uri('/search/')}?q={{search_term_string}}",
                "query-input": "required name=search_term_string"
            }
        }
        return {
            "title": f"{blog_setting.site_name} | {blog_setting.site_description}",
            "description": blog_setting.site_description,
            "keywords": blog_setting.site_keywords,
            "meta_tags": "",
            "json_ld": structured_data
        }

    def dispatch_seo_generation(self, metas, context):
        request = context.get('request')
        if not request:
            return metas

        view_name = request.resolver_match.view_name
        blog_setting = get_blog_setting()
        
        seo_data = None
        if view_name == 'blog:detailbyid':
            seo_data = self._get_article_seo_data(context, request, blog_setting)
        elif view_name == 'blog:category_detail':
            seo_data = self._get_category_seo_data(context, request, blog_setting)
        
        if not seo_data:
             seo_data = self._get_default_seo_data(context, request, blog_setting)

        json_ld_script = f'<script type="application/ld+json">{json.dumps(seo_data.get("json_ld", {}), ensure_ascii=False, indent=4)}</script>'

        return f"""
        <title>{seo_data.get("title", "")}</title>
        <meta name="description" content="{seo_data.get("description", "")}">
        <meta name="keywords" content="{seo_data.get("keywords", "")}">
        {seo_data.get("meta_tags", "")}
        {json_ld_script}
        """

plugin = SeoOptimizerPlugin()
