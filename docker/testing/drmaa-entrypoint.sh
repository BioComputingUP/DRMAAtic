#!/bin/bash
set -e

if [ "$1" = "runserver" ]
then
    echo "---> Starting the MUNGE Authentication service (munged) ..."
    gosu munge /usr/sbin/munged

    echo "---> Waiting for slurmctld to become active before starting slurmd..."

    until 2>/dev/null >/dev/tcp/slurmctld/6817
    do
        echo "-- slurmctld is not available.  Sleeping ..."
        sleep 2
    done
    echo "-- slurmctld is now active ..."

    echo "---> Resetting the drmaatic database ..."
    mysql -h mysql -P 3306 -u root -ppwd -e "DROP DATABASE IF EXISTS drmaatic; CREATE DATABASE drmaatic;"

    echo "---> Importing the test database bootstrap ..."
    mysql -h mysql -P 3306 -u root -ppwd < ./docker/testing/drmaatic_test.sql

    echo "---> Applying Django migrations ..."
    /opt/venv/bin/python manage.py migrate --noinput

    echo "---> Ensuring the admin user exists ..."
    /opt/venv/bin/python manage.py shell <<'PY'
from drmaatic.models import Admin

if not Admin.objects.filter(username='admin').exists():
    Admin.objects.create_superuser(username='admin', password='admin')
PY

    echo "---> Starting the django application ..."
    exec /opt/venv/bin/python manage.py runserver 0.0.0.0:8300
fi

exec "$@"
