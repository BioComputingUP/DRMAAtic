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
      mysql --host=mysql --port=3306 --user=root --password=pwd < ./docker/testing/drmaatic_test.sql 2>/dev/null
    } || {
      echo "-- The test database already exists ..."
    }

    echo "---> Starting the django application ..."
    exec /opt/venv/bin/python manage.py runserver 0.0.0.0:8300
fi

exec "$@"
