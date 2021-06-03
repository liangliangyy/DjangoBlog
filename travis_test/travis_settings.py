from DjangoBlog.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoblog',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': 'django_cache',
    }
}
