#!/bin/bash
set -e

if [ "$1" = "runserver" ]; then
  # Collect static files
  echo "---> Collecting static files ..."
  gosu django /opt/venv/bin/python3.8 manage.py collectstatic --noinput

  echo "---> Starting the MUNGE Authentication service (munged) ..."
  gosu munge /usr/sbin/munged

  echo "---> Starting Apache service ..."
  exec apachectl -D FOREGROUND
fi

exec "$@"
