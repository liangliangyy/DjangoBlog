FROM python:3.8-alpine

ARG DJANGO_SU_EMAIL=admin@blogd.com
ARG DJANGO_SU_PASSWORD=1qazXSW@
ARG DJANGO_SU_NAME=admin

ARG PGPASSWORD=blogd
ARG PGUSER=blogd
ARG PGNAME=blogd
ARG PGHOST=127.0.0.1

ARG MAKEMIGRATIONS=true
ARG MIGRATE=true
ARG COLLECT_STATIC=true
ARG COMPRESS_STATIC=true

RUN mkdir -p /opt/blogd
COPY requirements.txt /tmp/requirements.txt
RUN addgroup -g 101 blogd                                        &&  \
    adduser -G blogd -u 101 -h /opt/blogd -s /bin/sh -D blogd    &&  \
    chown -R 101:101 /opt/blogd && \
    apk add --no-cache --virtual .build-deps zlib-dev gcc libc-dev libffi-dev postgresql-dev g++ && \
    apk add memcached libssl1.1 libcrypto1.1 libpq postgresql-client git && \
    pip install -U pip django==2.2.8 && \
    pip install -Ur /tmp/requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*
COPY blogd.sh /blogd.sh
USER blogd
ENV DJANGO_SU_EMAIL=$DJANGO_SU_EMAIL \
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
WORKDIR /opt/blogd
ENTRYPOINT ["/blogd.sh"]
