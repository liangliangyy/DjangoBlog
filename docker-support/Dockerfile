FROM alpine:3.11
WORKDIR /app

COPY ./requirements.txt .

RUN apk --update --no-cache add python3 py3-pip py-gunicorn nginx mariadb-connector-c \
    && apk --update --no-cache add --virtual .build-deps \
        tzdata \
        # mysqlclient dependencies
        python3-dev \
		mariadb-connector-c-dev \
		gcc \
		musl-dev \
		# Pillow dependencies
        jpeg-dev \
        zlib-dev \
        freetype-dev \
        lcms2-dev \
        openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
        harfbuzz-dev \
        fribidi-dev \
	&& pip3 install --upgrade pip setuptools gevent \
	&& mkdir -p /run/nginx \
    && pip3 install -r requirements.txt \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del .build-deps

COPY . .
RUN python3 manage.py collectstatic --noinput \
    && python3 manage.py compress --force

COPY ./docker-support/nginx.conf /etc/nginx/conf.d/default.conf

ENV DJANGO_DEBUG False
ENV DJANGO_SECRET_KEY DJANGO_BLOG_CHANGE_ME

ENV DJANGO_MYSQL_DATABASE djangoblog
ENV DJANGO_MYSQL_USER root
ENV DJANGO_MYSQL_PASSWORD djangoblog_123
ENV DJANGO_MYSQL_HOST 127.0.0.1
ENV DJANGO_MYSQL_PORT 3306

ENV DJANGO_MEMCACHED_ENABLE True
ENV DJANGO_MEMCACHED_LOCATION 127.0.0.1:11211

ENV DJANGO_BAIDU_NOTIFY_URL http://data.zz.baidu.com/urls?site=https://www.example.org&token=CHANGE_ME

ENV DJANGO_EMAIL_TLS False
ENV DJANGO_EMAIL_SSL True
ENV DJANGO_EMAIL_HOST smtp.example.org
ENV DJANGO_EMAIL_PORT 465
ENV DJANGO_EMAIL_USER SMTP_USER_CHANGE_ME
ENV DJANGO_EMAIL_PASSWORD SMTP_PASSWORD_CHANGE_ME

ENV DJANGO_ADMIN_EMAIL admin@example.org

ENV DJANGO_WXADMIN_PASSWORD DJANGO_BLOG_CHANGE_ME
ENV DJANGO_WEROBOT_TOKEN DJANGO_BLOG_CHANGE_ME

EXPOSE 80
ENTRYPOINT ["./docker-support/entrypoint.sh"]