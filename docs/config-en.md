# Introduction to Main Features Settings

## Cache Configuration

The cache uses `localmem` (local memory cache) by default. If you have a Redis environment, you can automatically switch to Redis cache by setting the `DJANGO_REDIS_URL` environment variable.

### Using Redis Cache

Set the environment variable:
```bash
export DJANGO_REDIS_URL="127.0.0.1:6379/0"
```

Or directly modify the cache configuration in `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
    }
}
```

Reference code: https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L201-L215

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

## Update & Version Notes

### Database Migration Errors
If you encounter errors while executing database migrations:
```python
django.db.migrations.exceptions.MigrationSchemaMissing: Unable to create the django_migrations table ((1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '(6) NOT NULL)' at line 1"))
```
This problem may be caused by MySQL version < 5.6. Please upgrade to MySQL >= 5.6.

### Django Version Configuration

#### Django 4.0+ CSRF Configuration

Django 4.0 and above require `CSRF_TRUSTED_ORIGINS` configuration, otherwise you may encounter CSRF errors during login.

Configure your domain in `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'http://example.com',
    'https://example.com',
    'http://www.example.com',
    'https://www.example.com',
]
```

**Note**: Replace `example.com` with your actual domain, including the protocol (http/https).

Reference code: https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L41

#### Django 5.2 Notes

This project currently uses Django 5.2.9, which has been thoroughly tested and runs stably. If upgrading from an older version, please note:
- Ensure Python version >= 3.10
- Run database migrations: `python manage.py migrate`
- Update dependencies: `pip install -r requirements.txt`

