import logging

from django.utils import timezone

from djangoblog.utils import cache, get_blog_setting
from .models import Category, Article

logger = logging.getLogger(__name__)


def seo_processor(requests):
    key = 'seo_processor'
    value = cache.get(key)
    if value:
        return value
    else:
        logger.info('set processor cache.')
        setting = get_blog_setting()
        value = {
            'SITE_NAME': setting.site_name,
            'SHOW_GOOGLE_ADSENSE': setting.show_google_adsense,
            'GOOGLE_ADSENSE_CODES': setting.google_adsense_codes,
            'SITE_SEO_DESCRIPTION': setting.site_seo_description,
            'SITE_DESCRIPTION': setting.site_description,
            'SITE_KEYWORDS': setting.site_keywords,
            'SITE_BASE_URL': requests.scheme + '://' + requests.get_host() + '/',
            'ARTICLE_SUB_LENGTH': setting.article_sub_length,
            'nav_category_list': Category.objects.all(),
            'nav_pages': Article.objects.filter(
                type='p',
                status='p'),
            'OPEN_SITE_COMMENT': setting.open_site_comment,
            'BEIAN_CODE': setting.beian_code,
            'ANALYTICS_CODE': setting.analytics_code,
            "BEIAN_CODE_GONGAN": setting.gongan_beiancode,
            "SHOW_GONGAN_CODE": setting.show_gongan_code,
            "CURRENT_YEAR": timezone.now().year,
            "GLOBAL_HEADER": setting.global_header,
            "GLOBAL_FOOTER": setting.global_footer,
            "COMMENT_NEED_REVIEW": setting.comment_need_review,
        }
        cache.set(key, value, 60 * 60 * 10)
        return value
