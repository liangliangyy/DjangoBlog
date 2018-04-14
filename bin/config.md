# 主要功能配置介绍:

## 缓存：
缓存默认使用`memcache`缓存，如果你没有`memcache`环境，则将`settings.py`中的`locmemcache`改为`default`,并删除默认的`default`配置即可。
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'django_test' if TESTING else 'djangoblog',
        'TIMEOUT': 60 * 60 * 10
    },
    'locmemcache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 10800,
        'LOCATION': 'unique-snowflake',
    }
}
```
## oauth登录:

现在已经支持微博，Google，GitHub，Facebook登录，需要在其对应的开放平台申请oauth登录权限，然后修改`settings.py`中的如下配置:
```python
OAHUTH = {
    'sina': {
        'appkey': os.environ.get('SINA_APP_KEY'),
        'appsecret': os.environ.get('SINA_APP_SECRET'),
        'callbackurl': 'http://www.lylinux.net/oauth/authorize?type=weibo'
    },
    'google': {
        'appkey': os.environ.get('GOOGLE_APP_KEY'),
        'appsecret': os.environ.get('GOOGLE_APP_SECRET'),
        'callbackurl': 'http://www.lylinux.net/oauth/authorize?type=google'
    },
    'github': {
        'appkey': os.environ.get('GITHUB_APP_KEY'),
        'appsecret': os.environ.get('GITHUB_APP_SECRET'),
        'callbackurl': 'http://www.lylinux.net/oauth/authorize?type=github'
    },
    'facebook': {
        'appkey': os.environ.get('FACEBOOK_APP_KEY'),
        'appsecret': os.environ.get('FACEBOOK_APP_SECRET'),
        'callbackurl': 'http://www.lylinux.net/oauth/authorize?type=facebook'
    }
}
```
将对应的appkey和appsecret修改为你自己的，将`callbackurl`的域名也修改为你的域名。
## Update Oauth配置部分已经修改到配置表中

## owntracks：
owntracks是一个位置追踪软件，可以定时的将你的坐标提交到你的服务器上，现在简单的支持owntracks功能，需要安装owntracks的app，然后将api地址设置为:
`你的域名/owntracks/logtracks`就可以了。然后访问`你的域名/owntracks/show_dates`就可以看到有经纬度记录的日期，点击之后就可以看到运动轨迹了。地图是使用高德地图绘制。

## 邮件功能：
同样，将`settings.py`中的`ADMINS = [('liangliang', 'liangliangyy@gmail.com')]`配置为你自己的错误接收邮箱，另外修改:
```python
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = os.environ.get('DJANGO_EMAIL_USER')
```
为你自己的邮箱配置。

## 微信公众号
集成了简单的微信公众号功能，在微信后台将token地址设置为:`你的域名/robot` 即可，默认token为`lylinux`，当然你可以修改为你自己的，在`servermanager/robot.py`中。
