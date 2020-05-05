FROM python:3.8-alpine

ARG DJANGO_SU_EMAIL=admin@blogd.com
ARG DJANGO_SU_PASSWORD=1q2w3e!
ARG DJANGO_SU_NAME=admin
ARG BRANCH=master
ARG PGPASSWORD=blogd
ARG PGUSER=blogd
ARG PGNAME=blogd
ARG PGHOST=postgres
ARG MAKEMIGRATIONS=true
ARG MIGRATE=true
ARG COLLECT_STATIC=true
ARG BLOGD_REPO_URL=https://github.com/mtuktarov/mtuktarov.ru.git
ARG COMPRESS_STATIC=true
ENV BRANCH=$BRANCH \
    DJANGO_SU_EMAIL=$DJANGO_SU_EMAIL \
    DJANGO_SU_PASSWORD=$DJANGO_SU_PASSWORD \
    DJANGO_SU_NAME=$DJANGO_SU_NAME \
    PGPASSWORD=$PGPASSWORD \
    PGUSER=$PGUSER \
    PGNAME=$PGNAME \
    PGHOST=$PGHOST \
    MAKEMIGRATIONS=$MAKEMIGRATIONS \
    MIGRATE=$MIGRATE \
    COLLECT_STATIC=$COLLECT_STATIC \
    COMPRESS_STATIC=$COMPRESS_STATIC

COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache --virtual .build-deps zlib-dev gcc libc-dev libffi-dev postgresql-dev \
            openssl-dev jpeg-dev zlib-dev libxml2-dev libxslt-dev musl-dev freetype-dev \
            lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev  \
    && apk add memcached libssl1.1 libcrypto1.1 libpq libgcc postgresql-client libxml2 git \
    && pip install --no-cache-dir -Ur /tmp/requirements.txt \
    && git clone -b $BRANCH $BLOGD_REPO_URL /opt/blogd \
    && mkdir -p /opt/blogd/socket /opt/blogd/media /opt/blogd/static \
    && apk del .build-deps git \
    && rm -rf /var/cache/apk/*  /tmp/requirements.txt \
    && mv /opt/blogd/media  /opt/blogd/media_tmp \
    && addgroup -g 1000 blogd                                      \
    && adduser -G blogd -u 1000 -h /opt/blogd -s /bin/sh -D blogd  \
    && chown -R 1000:1000 /opt/blogd
USER blogd

WORKDIR /opt/blogd
ENTRYPOINT ["/opt/blogd/blogd.sh"]