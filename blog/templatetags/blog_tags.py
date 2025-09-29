import hashlib
import logging
import random
import urllib

from django import template
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

from blog.models import Article, Category, Tag, Links, SideBar, LinkShowType
from comments.models import Comment
from djangoblog.utils import CommonMarkdown, sanitize_html
from djangoblog.utils import cache
from djangoblog.utils import get_current_site
from oauth.models import OAuthUser
from djangoblog.plugin_manage import hooks

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def head_meta(context):
    return mark_safe(hooks.apply_filters('head_meta', '', context))


@register.simple_tag
def timeformat(data):
    try:
        return data.strftime(settings.TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.filter()
@stringfilter
def custom_markdown(content):
    html_content = CommonMarkdown.get_markdown(content)
    
    # 然后应用插件过滤器优化HTML
    from djangoblog.plugin_manage import hooks
    from djangoblog.plugin_manage.hook_constants import ARTICLE_CONTENT_HOOK_NAME
    optimized_html = hooks.apply_filters(ARTICLE_CONTENT_HOOK_NAME, html_content)
    
    return mark_safe(optimized_html)


@register.simple_tag(takes_context=True)
def render_article_content(context, article, is_summary=False):
    """
    渲染文章内容，包含完整的上下文信息供插件使用
    
    Args:
        context: 模板上下文
        article: 文章对象
        is_summary: 是否为摘要模式（首页使用）
    """
    if not article or not hasattr(article, 'body'):
        return ''
    
    # 先转换Markdown为HTML
    html_content = CommonMarkdown.get_markdown(article.body)
    
    # 如果是摘要模式，先截断内容再应用插件
    if is_summary:
        # 截断HTML内容到合适的长度（约300字符）
        from django.utils.html import strip_tags
        from django.template.defaultfilters import truncatechars
        
        # 先去除HTML标签，截断纯文本，然后重新转换为HTML
        plain_text = strip_tags(html_content)
        truncated_text = truncatechars(plain_text, 300)
        
        # 重新转换截断后的文本为HTML（简化版，避免复杂的插件处理）
        html_content = CommonMarkdown.get_markdown(truncated_text)
    
    # 然后应用插件过滤器，传递完整的上下文
    from djangoblog.plugin_manage import hooks
    from djangoblog.plugin_manage.hook_constants import ARTICLE_CONTENT_HOOK_NAME
    
    # 获取request对象
    request = context.get('request')
    
    # 应用所有文章内容相关的插件
    # 注意：摘要模式下某些插件（如版权声明）可能不适用
    optimized_html = hooks.apply_filters(
        ARTICLE_CONTENT_HOOK_NAME, 
        html_content, 
        article=article, 
        request=request,
        context=context,
        is_summary=is_summary  # 传递摘要标志，插件可以据此调整行为
    )
    
    return mark_safe(optimized_html)


@register.simple_tag
def get_markdown_toc(content):
    from djangoblog.utils import CommonMarkdown
    body, toc = CommonMarkdown.get_markdown_with_toc(content)
    return mark_safe(toc)


@register.filter()
@stringfilter
def comment_markdown(content):
    content = CommonMarkdown.get_markdown(content)
    return mark_safe(sanitize_html(content))


@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    获得文章内容的摘要
    :param content:
    :return:
    """
    from django.template.defaultfilters import truncatechars_html
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    return truncatechars_html(content, blogsetting.article_sub_length)


@register.filter(is_safe=True)
@stringfilter
def truncate(content):
    from django.utils.html import strip_tags

    return strip_tags(content)[:150]


@register.inclusion_tag('blog/tags/breadcrumb.html')
def load_breadcrumb(article):
    """
    获得文章面包屑
    :param article:
    :return:
    """
    names = article.get_category_tree()
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    site = get_current_site().domain
    names.append((blogsetting.site_name, '/'))
    names = names[::-1]

    return {
        'names': names,
        'title': article.title,
        'count': len(names) + 1
    }


@register.inclusion_tag('blog/tags/article_tag_list.html')
def load_articletags(article):
    """
    文章标签
    :param article:
    :return:
    """
    tags = article.tags.all()
    tags_list = []
    for tag in tags:
        url = tag.get_absolute_url()
        count = tag.get_article_count()
        tags_list.append((
            url, count, tag, random.choice(settings.BOOTSTRAP_COLOR_TYPES)
        ))
    return {
        'article_tags_list': tags_list
    }


@register.inclusion_tag('blog/tags/sidebar.html')
def load_sidebar(user, linktype):
    """
    加载侧边栏
    :return:
    """
    value = cache.get("sidebar" + linktype)
    if value:
        value['user'] = user
        return value
    else:
        logger.info('load sidebar')
        from djangoblog.utils import get_blog_setting
        blogsetting = get_blog_setting()
        recent_articles = Article.objects.filter(
            status='p')[:blogsetting.sidebar_article_count]
        sidebar_categorys = Category.objects.all()
        extra_sidebars = SideBar.objects.filter(
            is_enable=True).order_by('sequence')
        most_read_articles = Article.objects.filter(status='p').order_by(
            '-views')[:blogsetting.sidebar_article_count]
        dates = Article.objects.datetimes('creation_time', 'month', order='DESC')
        links = Links.objects.filter(is_enable=True).filter(
            Q(show_type=str(linktype)) | Q(show_type=LinkShowType.A))
        commment_list = Comment.objects.filter(is_enable=True).order_by(
            '-id')[:blogsetting.sidebar_comment_count]
        # 标签云 计算字体大小
        # 根据总数计算出平均值 大小为 (数目/平均值)*步长
        increment = 5
        tags = Tag.objects.all()
        sidebar_tags = None
        if tags and len(tags) > 0:
            s = [t for t in [(t, t.get_article_count()) for t in tags] if t[1]]
            count = sum([t[1] for t in s])
            dd = 1 if (count == 0 or not len(tags)) else count / len(tags)
            import random
            sidebar_tags = list(
                map(lambda x: (x[0], x[1], (x[1] / dd) * increment + 10), s))
            random.shuffle(sidebar_tags)

        value = {
            'recent_articles': recent_articles,
            'sidebar_categorys': sidebar_categorys,
            'most_read_articles': most_read_articles,
            'article_dates': dates,
            'sidebar_comments': commment_list,
            'sidabar_links': links,
            'show_google_adsense': blogsetting.show_google_adsense,
            'google_adsense_codes': blogsetting.google_adsense_codes,
            'open_site_comment': blogsetting.open_site_comment,
            'show_gongan_code': blogsetting.show_gongan_code,
            'sidebar_tags': sidebar_tags,
            'extra_sidebars': extra_sidebars
        }
        cache.set("sidebar" + linktype, value, 60 * 60 * 60 * 3)
        logger.info('set sidebar cache.key:{key}'.format(key="sidebar" + linktype))
        value['user'] = user
        return value


@register.inclusion_tag('blog/tags/article_meta_info.html')
def load_article_metas(article, user):
    """
    获得文章meta信息
    :param article:
    :return:
    """
    return {
        'article': article,
        'user': user
    }


@register.inclusion_tag('blog/tags/article_pagination.html')
def load_pagination_info(page_obj, page_type, tag_name):
    previous_url = ''
    next_url = ''
    if page_type == '':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse('blog:index_page', kwargs={'page': next_number})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:index_page', kwargs={
                    'page': previous_number})
    if page_type == '分类标签归档':
        tag = get_object_or_404(Tag, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': next_number,
                    'tag_name': tag.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': previous_number,
                    'tag_name': tag.slug})
    if page_type == '作者文章归档':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': next_number,
                    'author_name': tag_name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': previous_number,
                    'author_name': tag_name})

    if page_type == '分类目录归档':
        category = get_object_or_404(Category, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': next_number,
                    'category_name': category.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': previous_number,
                    'category_name': category.slug})

    return {
        'previous_url': previous_url,
        'next_url': next_url,
        'page_obj': page_obj
    }


@register.inclusion_tag('blog/tags/article_info.html')
def load_article_detail(article, isindex, user):
    """
    加载文章详情
    :param article:
    :param isindex:是否列表页，若是列表页只显示摘要
    :return:
    """
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()

    return {
        'article': article,
        'isindex': isindex,
        'user': user,
        'open_site_comment': blogsetting.open_site_comment,
    }


# 返回用户头像URL
# 模板使用方法:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    """获得用户头像 - 优先使用OAuth头像，否则使用默认头像"""
    cachekey = 'avatar/' + email
    url = cache.get(cachekey)
    if url:
        return url
    
    # 检查OAuth用户是否有自定义头像
    usermodels = OAuthUser.objects.filter(email=email)
    if usermodels:
        # 过滤出有头像的用户
        users_with_picture = list(filter(lambda x: x.picture is not None, usermodels))
        if users_with_picture:
            # 获取默认头像路径用于比较
            default_avatar_path = static('blog/img/avatar.png')
            
            # 优先选择非默认头像的用户，否则选择第一个
            non_default_users = [u for u in users_with_picture if u.picture != default_avatar_path and not u.picture.endswith('/avatar.png')]
            selected_user = non_default_users[0] if non_default_users else users_with_picture[0]
            
            url = selected_user.picture
            cache.set(cachekey, url, 60 * 60 * 24)  # 缓存24小时
            
            avatar_type = 'non-default' if non_default_users else 'default'
            logger.info('Using {} OAuth avatar for {} from {}'.format(avatar_type, email, selected_user.type))
            return url
    
    # 使用默认头像
    url = static('blog/img/avatar.png')
    cache.set(cachekey, url, 60 * 60 * 24)  # 缓存24小时
    logger.info('Using default avatar for {}'.format(email))
    return url


@register.filter
def gravatar(email, size=40):
    """获得用户头像HTML标签"""
    url = gravatar_url(email, size)
    return mark_safe(
        '<img src="%s" height="%d" width="%d" class="avatar" alt="用户头像">' %
        (url, size, size))


@register.simple_tag
def query(qs, **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
