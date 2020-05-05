#!/usr/bin/env sh
TEST_SERVER_SOCKET=${TEST_SERVER_SOCKET:-0.0.0.0:8000}
UWSGI_PARAMS=${UWSGI_PARAMS:---ini ./blogd.ini}

format_arg(){
    echo ${1:-false} | tr [A-Z] [a-z]
}

[ $(format_arg $EXEC_MODE) = true ] && /bin/sh || {

    [ $(format_arg $WAIT_FOR_POSTGRES) = true ] && {
        while true ; do
            psql -c "SELECT datname FROM pg_database WHERE datistemplate = false;" && break || sleep 10
        done
    }
    cp /opt/blogd/config/local_settings.py /opt/blogd/DjangoBlog/local_settings.py
    cp -R /opt/blogd/media_tmp/* /opt/blogd/media
    [ $(format_arg $MAKEMIGRATIONS) = true ] && /opt/blogd/manage.py makemigrations
    [ $(format_arg $MIGRATE) = true ] && /opt/blogd/manage.py migrate
    [ $(format_arg $ADD_SUPERUSER) = true ] && /opt/blogd/manage.py add_superuser
    [ $(format_arg $CONFIGURE_GROUPS) = true ] && /opt/blogd/manage.py configure_groups
    [ $(format_arg $RENAME_SITE) = true ] && /opt/blogd/manage.py rename_site
    [ $(format_arg $COLLECT_STATIC) = true ] && /opt/blogd/manage.py collectstatic --noinput
    [ $(format_arg $COMPRESS_STATIC) = true ] && /opt/blogd/manage.py compress --force
    [ $(format_arg $DJANGO_DISABLE_CACHE) = true ] ||  memcached -d
    [ $(format_arg $TEST_SERVER) = true ] && /opt/blogd/manage.py runserver ${TEST_SERVER_SOCKET} ||
        uwsgi $UWSGI_PARAMS
}
