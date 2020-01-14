FROM python:3.8-alpine

CMD mkdir -p /opt/blogd
COPY accounts /opt/blogd/accounts
COPY DjangoBlog /opt/blogd/DjangoBlog
COPY blog /opt/blogd/blog
COPY comments /opt/blogd/comments
COPY oauth /opt/blogd/oauth
COPY owntracks /opt/blogd/owntracks
COPY servermanager /opt/blogd/servermanager
COPY templates /opt/blogd/templates
COPY *.py  /opt/blogd/
COPY *.txt /opt/blogd/
COPY *.ini /opt/blogd/
WORKDIR /opt/blogd
RUN apk add --no-cache --virtual .build-deps jpeg-dev zlib-dev gcc libc-dev libffi-dev postgresql-dev && \
    pip install -U pip && \
    pip install -Ur requirements.txt && \
    addgroup -g 101 blogd                                        &&  \
    adduser -G blogd -u 101 -h /opt/blogd -s /bin/sh -D blogd    &&  \
    chown -R 101:101 /opt/blogd && \
    apk del --update gcc libc-dev libffi-dev zlib-dev postgresql-dev && \
    rm -rf /var/cache/apk/*
USER blogd

#CMD [ "/bin/sh", "-c", "uwsgi --ini ./blogd.ini" ]
