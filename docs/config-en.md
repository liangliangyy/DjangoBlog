# Introduction to main features settings

## Cache:
Cache using `memcache` for default. If you don't have `memcache` environment, you can remove the `default` setting in `CACHES` and change `locmemcache` to `default`.
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

## OAuth Login:
QQ, Weibo, Google, GitHub and Facebook are now supported for OAuth login. Fetch OAuth login permissions from the corresponding open platform, and save them with `appkey`, `appsecret` and callback address in **Backend->OAuth** configuration.

### Callback address examples:
QQ: http://your-domain-name/oauth/authorize?type=qq
Weibo: http://your-domain-name/oauth/authorize?type=weibo
type is in the type field of `oauthmanager`.

## owntracks:
owntracks is a location tracking application. It will send your locaiton to the server by timing.Simple support owntracks features. Just install owntracks app and set api address as `your-domain-name/owntracks/logtracks`. Visit `your-domain-name/owntracks/show_dates` and you will see the date with latitude and langitude, click it and see the motion track. The map is drawn by AMap.

## Email feature:
Same as before, Configure your own error msg recvie email information with`ADMINS = [('liangliang', 'liangliangyy@gmail.com')]` in `settings.py`. And modify:
```python
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = os.environ.get('DJANGO_EMAIL_USER')
```
with your email account information.

## WeChat Official Account
Simple wechat official account features integrated. Set token as `your-domain-name/robot` in wechat backend. Default token is `lylinux`, you can change it to your own in `servermanager/robot.py`. Add a new command in `Backend->Servermanager->command`, in this way, you can manage the system through wechat official account.

## Introduction to website configuration
You can add website configuration in **Backend->BLOG->WebSiteConfiguration**. Such as: keywords, description, Google Ad, website stats code, case number, etc.
OAuth user avatar path is saved in *StaticFileSavedAddress*. Please input absolute path, code directory for default.

## Source code highlighting
If the code block in your article didn't show hightlight, please write the code blocks as following:

![](https://resource.lylinux.net/image/codelang.png)

That is, you should add the corresponding language name before the code block.

## Update
If you get errors as following while executing database migrations:
```python
django.db.migrations.exceptions.MigrationSchemaMissing: Unable to create the django_migrations table ((1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '(6) NOT NULL)' at line 1"))
```
This problem may cause by the mysql version under 5.6, a new version( >= 5.6 ) mysql is needed.

