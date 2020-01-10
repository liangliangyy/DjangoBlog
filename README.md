# DjangoBlog

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
- Wechat official account feature integrated. Now, you can use wechat official account to manage your VPS.

## Installation
Install via pip: `pip install -Ur requirements.txt`

### Configuration
Most configurations are in `setting.py`, others are in backend configurations.

I set many `setting` configuration with my environment variables (such as: `SECRET_KEY`, `OAUTH`, `mysql` and some email configuration parts.) and they did NOT been submitted to the `GitHub`. You can change these in the code with your own configuration or just add them into your environment variables.

Files in `test` directory are for `travis` with automatic testing. You do not need to care about this. Or just use it, in this way to integrate `travis` for automatic testing.

In `bin` directory, we have scripts to deploy with `Nginx`+`Gunicorn`+`virtualenv`+`supervisor` on `linux` and `Nginx` configuration file.

## Run

Modify `DjangoBlog/setting.py` with database settings, as following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mtuktarov',
        'USER': 'mtuktarov',
        'PASSWORD': 'mypass_mtuktarov',
        'HOST': 'host',
    }
}
```

### Create database
Run the following command in MySQL shell:
```sql
CREATE USER mtuktarov WITH ENCRYPTED PASSWORD 'mypass_mtuktarov';
CREATE DATABASE mtuktarov TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE mtuktarov TO mtuktarov;
```

Run the following commands in Terminal:
```bash
./manage.py makemigrations
./manage.py migrate
```

**Attention: ** Before you using `./manage.py`, make sure the `python` command in your system is towards to `python 3.6` or above version. Otherwise you may solve this by one of the two following methods:
- Modify the first line in `manage.py`, change `#!/usr/bin/env python` to `#!/usr/bin/env python3`
- Just run with: `python3 ./manage.py makemigrations`

### Create super user

Run command in terminal:
```bash
./manage.py createsuperuser
```

### Create testing data
Run command in terminal:
```bash
./manage.py create_testdata
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

## More configurations
[More configurations details](/docs/config-en.md)
