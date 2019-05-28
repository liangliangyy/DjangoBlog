from DjangoBlog.settings import *

SECRET_KEY = '&3g0bdza#c%dm1lf%5gi&0-*53p3t0m*hmcvo29cn^$ji7je(c'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


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
