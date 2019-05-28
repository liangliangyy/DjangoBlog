from DjangoBlog.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoblog',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        # 'HOST': '192.168.1.120',
        # 'USER': 'root',
        # 'PASSWORD': 'root',
        'PORT': 3306,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': 'django_cache',
    }
}
