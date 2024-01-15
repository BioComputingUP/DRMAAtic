#!/bin/bash
set -e

if [ "$1" = "runserver" ]
then
    echo "---> Starting the MUNGE Authentication service (munged) ..."
    gosu munge /usr/sbin/munged

    echo "---> Starting the django application ..."
    exec /opt/venv/bin/python manage.py runserver 0.0.0.0:8300
fi

exec "$@"
