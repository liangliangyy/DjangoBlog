ARTICLE_DETAIL_LOAD = 'article_detail_load'
ARTICLE_CREATE = 'article_create'
ARTICLE_UPDATE = 'article_update'
ARTICLE_DELETE = 'article_delete'

ARTICLE_CONTENT_HOOK_NAME = "the_content"

# 位置钩子常量
POSITION_HOOKS = {
    'article_top': 'article_top_widgets',
    'article_bottom': 'article_bottom_widgets',
    'sidebar': 'sidebar_widgets',
    'header': 'header_widgets',
    'footer': 'footer_widgets',
    'comment_before': 'comment_before_widgets',
    'comment_after': 'comment_after_widgets',
}

# 资源注入钩子
HEAD_RESOURCES_HOOK = 'head_resources'
BODY_RESOURCES_HOOK = 'body_resources'

