#!/usr/bin/env python
# encoding: utf-8

from djangoblog.settings import *
import os

# 自定义Compressor配置 - 解决CDN URL问题
from compressor.conf import CompressorConf

class CDNCompressorConf(CompressorConf):
    """压缩时强制使用本地路径"""
    def configure_url(self, value):
        return getattr(__import__('django.conf', fromlist=['settings']).settings, 'COMPRESS_URL', '/static/')
    
    def configure_root(self, value):
        return getattr(__import__('django.conf', fromlist=['settings']).settings, 'COMPRESS_ROOT', None)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = ['www.lylinux.net', 'lylinux.net',
                 '127.0.0.1', '*.lylinux.net', '*']

INSTALLED_APPS = [
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'mdeditor',
    'haystack',
    'blog',
    'accounts',
    'comments',
    'oauth',
    'servermanager',
    'owntracks',
    'compressor',
    'djangoblog',
]

PAGINATE_BY = 6
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379',
        'TIMEOUT': 60 * 60 * 10
    },
    'locmemcache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 10800,
        'LOCATION': 'unique-snowflake',
    }
}

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 587

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'log_file'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d %(module)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'djangoblog.log'),
            'when': 'D',
            'formatter': 'verbose',
            'interval': 1,
            'delay': True,
            'backupCount': 5,
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'origin.lylinux.net',
            'port': 5000,
            'version': 1,
            'message_type': 'django',
            'fqdn': False,
            'tags': ['django'],
        }
    },
    'loggers': {
        'djangoblog': {
            'handlers': ['log_file', 'console', 'logstash'],
            'level': 'INFO',
            'propagate': True,
        },
        'DjangoBlog': {
            'handlers': ['log_file', 'console', 'logstash'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'logstash'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['mail_admins', 'logstash'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

X_FRAME_OPTIONS = 'DENY'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

STATIC_URL = 'https://resource.lylinux.net/djangoblog/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/media/'

# Django Compressor 配置 - 使用自定义配置类
COMPRESS_CONF = 'djangoblog.settings_prod.CDNCompressorConf'
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True  # 启用离线压缩
COMPRESS_OFFLINE_CONTEXT = {}  # 离线压缩上下文
COMPRESS_URL = '/static/'  # 压缩时使用本地路径
COMPRESS_ROOT = os.path.join(BASE_DIR, 'collectedstatic')
COMPRESS_OUTPUT_DIR = 'compressed'

# CSS/JS过滤器
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSCompressorFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.SlimItFilter',
]
# 安全头部配置 - 防XSS和其他攻击
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# 内容安全策略 (CSP) - 防XSS攻击
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'",
                  "cdn.mathjax.org", "*.googleapis.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'",
                 "*.googleapis.com", "*.gstatic.com"]
CSP_IMG_SRC = ["'self'", "data:", "*.lylinux.net",
               "*.gravatar.com", "*.githubusercontent.com"]
CSP_FONT_SRC = ["'self'", "*.googleapis.com", "*.gstatic.com"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_SRC = ["'none'"]
CSP_OBJECT_SRC = ["'none'"]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'djangoblog.elasticsearch_backend.ElasticSearchEngine',
    }
}
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}

ADMINS = [('admin', 'liangliangyy@gmail.com')]
CSRF_TRUSTED_ORIGINS = ['https://*.lylinux.net', 'https://*.127.0.0.1']
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
PLUGINS_DIR = BASE_DIR / 'plugins'
ACTIVE_PLUGINS = [
    'article_copyright',
    'reading_time',
    'external_links',
    'view_count',
    'seo_optimizer',
    'image_lazy_loading',
    'article_recommendation',
]
