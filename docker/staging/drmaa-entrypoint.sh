#!/bin/bash
set -e

if [ "$1" = "runserver" ]; then
  # Collect static files
  echo "---> Collecting static files ..."
#  gosu www-data /opt/venv/bin/python3.8 manage.py collectstatic --noinput

  # Apply database migrations
  echo "---> Applying database migrations ..."
  #gosu www-data /opt/venv/bin/python3.8 manage.py makemigrations
  #gosu www-data /opt/venv/bin/python3.8 manage.py migrate

  echo "---> Starting the MUNGE Authentication service (munged) ..."
#  gosu munge /usr/sbin/munged

  echo "---> Starting Apache service ..."
  exec apachectl -D FOREGROUND
fi

#exec "$@"
