#!/usr/bin/env sh
TEST_SERVER_SOCKET=${TEST_SERVER_SOCKET:-0.0.0.0:8000}
UWSGI_PARAMS=${UWSGI_PARAMS:---ini ./blogd.ini}
BRANCH=${BRANCH:-master}

format_arg(){
    echo ${1:-false} | tr [A-Z] [a-z]
}

[ $(format_arg $EXEC_MODE) = true ] && /bin/sh || {

    [ $(format_arg $WAIT_FOR_POSTGRES) = true ] && {
        while true ; do
            psql -c "SELECT datname FROM pg_database WHERE datistemplate = false;" && break || sleep 10
        done
    }

    [ -d /opt/blogd ] || mkdir -p /opt/blogd
    ls -a /opt/blogd | grep '.git' || git clone --single-branch --branch $BRANCH https://github.com/mtuktarov/mtuktarov.ru.git /opt/blogd

    cd /opt/blogd && git checkout $BRANCH && git pull origin $BRANCH
    mkdir -p /opt/blogd_sockets /opt/blogd_media
    ln -fs /opt/local_settings.py /opt/blogd/local_settings.py
    [ $(format_arg $MAKEMIGRATIONS) = true ] && ./manage.py makemigrations
    [ $(format_arg $MIGRATE) = true ] && ./manage.py migrate
    [ $(format_arg $ADD_SUPERUSER) = true ] && ./manage.py add_superuser
    [ $(format_arg $CONFIGURE_GROUPS) = true ] && ./manage.py configure_groups
    [ $(format_arg $RENAME_SITE) = true ] && ./manage.py rename_site
    [ $(format_arg $COLLECT_STATIC) = true ] && ./manage.py collectstatic --noinput
    [ $(format_arg $COMPRESS_STATIC) = true ] && ./manage.py compress --force
    [ $(format_arg $DJANGO_DISABLE_CACHE) = true ] ||  memcached -d
    [ $(format_arg $TEST_SERVER) = true ] && ./manage.py runserver ${TEST_SERVER_SOCKET} ||
        uwsgi $UWSGI_PARAMS
}
