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

    {
      echo "-- Importing the test database ..."
      mysql -h mysql -P 3306 -u root -ppwd < ./docker/testing/drmaatic_test.sql 2>/dev/null
    } || {
      echo "-- The test database already exists ..."
    }

    echo "---> Applying Django migrations ..."
    /opt/venv/bin/python manage.py migrate --noinput

    echo "---> Starting the django application ..."
    exec /opt/venv/bin/python manage.py runserver 0.0.0.0:8300
fi

exec "$@"
