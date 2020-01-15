FROM python:3.8-alpine

RUN mkdir -p /opt/blogd
WORKDIR /opt/blogd
COPY requirements.txt /opt/blogd/requirements.txt
RUN addgroup -g 101 blogd                                        &&  \
    adduser -G blogd -u 101 -h /opt/blogd -s /bin/sh -D blogd    &&  \
    chown -R 101:101 /opt/blogd && \
    apk add --no-cache --virtual .build-deps memcached jpeg-dev zlib-dev gcc libc-dev libffi-dev postgresql-dev g++ && \
    echo 'http://dl-cdn.alpinelinux.org/alpine/v3.8/main' >> /etc/apk/repositories && \
    apk add --no-cache libcrypto1.0 libssl1.0 && \
    pip install -U pip && \
    pip install -Ur requirements.txt && \
    apk del --update gcc libc-dev libffi-dev zlib-dev postgresql-dev && \
    rm -rf /var/cache/apk/*
USER blogd
CMD [ "/bin/sh", "-c", "./manage.py collectstatic --noinput ; ./manage.py compress --force ; memcached -d ; uwsgi --ini ./blogd.ini" ]
