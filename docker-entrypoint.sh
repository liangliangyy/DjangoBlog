#!/bin/sh

# shellcheck disable=SC2034
SOCKFILE=/tmp/gunicorn.sock

# shellcheck disable=SC2112
function init() {
    echo "init ...";
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --no-input
    python manage.py compress --force
    echo "init done."
}

# shellcheck disable=SC2112
function start() {
    echo "start server..."
    gunicorn DjangoBlog.wsgi:application --bind=0.0.0.0:8000 --name blog --workers 1 --log-level=debug
}

# shellcheck disable=SC2112
function main() {
    init
    sleep 2
    start

}

main $#