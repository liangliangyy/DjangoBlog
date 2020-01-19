# mtuktarov.ru blog

A blog system based on `python3.6` and `Django2.1`.

## Main Features:
- Articles, Pages, Categories, Tags(Add, Delete, Edit), edc. Articles and pages support `Markdown` and highlighting.
- Articles support full-text search.
- Complete comment feature, include posting reply comment and email notification. `Markdown` supporting.
- Sidebar feature: new articles, most readings, tags, etc.
- OAuth Login supported, including Google, GitHub, Facebook, Weibo, QQ.
- `Memcache` supported, with cache auto refresh.
- Simple SEO Features, notify Google and Baidu when there was a new article or other things.
- Simple picture bed feature integrated.
- `django-compressor` integrated, auto-compressed `css`, `js`.
- Website exception email notification. When there is an unhandle exception, system will send an email notification.

## Installation
Install via pip: `pip install -Ur requirements.txt`

### Configuration
Most configurations are in `setting.py`, others are in backend configurations.

To deploy blog, you will need to install docker and do the following:

1. Checkout blog to /opt/blog
2. Set up permissions:
```
chown -R 101:101 /opt/blogd
mkdir /opt/blogd/{data,sockets,ssl}
chmod 2775 /opt/blogd
```
3. Copy your ssl cert/key to the `/opt/blogd/ssl` direcotry and modify `/opt/blogd/config/nginx/mtuktarov.ru.conf` accordingly
4. Navigate to `/opt/blogd` and execute `docker build` command. Push to your repo and change `/opt/blogd/config/servcies/blogd.service` specifying correct docker imagename and tag.
5. Copy systemd unit files from `/opt/blogd/config/servcies` to `/etc/systemd/system`.

## Run

Modify `DjangoBlog/setting.py` with database settings or use environment variables, as following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJANGO_DB_NAME', 'mtuktarov'),
        'USER': os.getenv('DJANGO_DB_USER', 'mtuktarov'),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'mypass_mtuktarov'),
        'HOST': os.getenv('DJANGO_DB_HOST', '/opt/blogd/sockets'),
    }
}
```

### Create database
If you do not want to use postgresql container:
```sql
CREATE USER mtuktarov WITH ENCRYPTED PASSWORD 'mypass_mtuktarov';
CREATE DATABASE mtuktarov TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE mtuktarov TO mtuktarov;
```

Login to `blogd` container and run:
```bash
./manage.py makemigrations
./manage.py migrate
```

### Create super user

Run command in terminal:
```bash
./manage.py createsuperuser
```

### Collect static files
Run command in terminal:
```bash
./manage.py collectstatic --noinput
./manage.py compress --force
```

### Getting start to run server
Execute: `./manage.py runserver`

Open up a browser and visit: http://127.0.0.1:8000/ , the you will see the blog.

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

## Introduction to website configuration
You can add website configuration in **Backend->BLOG->WebSiteConfiguration**. Such as: keywords, description, Google Ad, website stats code, case number, etc.
OAuth user avatar path is saved in *StaticFileSavedAddress*. Please input absolute path, code directory for default.

## Source code highlighting
If the code block in your article didn't show hightlight, please write the code blocks as following:

![](https://resource.lylinux.net/image/codelang.png)

That is, you should add the corresponding language name before the code block.
