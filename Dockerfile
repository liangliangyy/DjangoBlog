FROM python:3.8-alpine

ENV LC_ALL=C.UTF-8
ENV REP_VERSION 3.11
ENV PYTHONUNBUFFERED 1
ENV DEBUG=false

COPY . /DjangoBlog/
COPY docker-entrypoint.sh /usr/local/bin/
WORKDIR /DjangoBlog

RUN set -x \
    && echo "https://mirrors.aliyun.com/alpine/v${REP_VERSION}/main" > /etc/apk/repositories \
    && echo "https://mirrors.aliyun.com/alpine/v${REP_VERSION}/community" >>/etc/apk/repositories \
    && apk --no-cache update \
    && apk add --no-cache tini \
    && apk add --no-cache --virtual temp-apks \
        g++ \
        gcc \
        make \
        musl-dev \
        libffi-dev \
        libxslt-dev \
        libressl-dev \
        openssl-dev \
        tzdata \
        python3-dev \
        mariadb-dev \
        zlib-dev\
        jpeg-dev \
    && chmod 755 /usr/local/bin/docker-entrypoint.sh \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && pip install --upgrade pip -i https://pypi.doubanio.com/simple \
    && pip install -r requirements.txt -i https://pypi.doubanio.com/simple \
    && apk del temp-apks \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache \
    && rm -rf /tmp/*

EXPOSE 8000

CMD ["docker-entrypoint.sh"]