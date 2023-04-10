FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install gcc default-libmysqlclient-dev -y \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime \
    && echo Asia/Shanghai > /etc/timezone

WORKDIR /code/djangoblog/

COPY requirements.txt requirements.txt

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -Ur requirements.txt  \
    && pip install gunicorn[gevent] \
    && pip cache purge
        
COPY . .

RUN chmod +x /code/djangoblog/bin/docker_start.sh

ENTRYPOINT ["/code/djangoblog/bin/docker_start.sh"]
