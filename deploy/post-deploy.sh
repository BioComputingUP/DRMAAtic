# This script is executed on the remote server after the code is updated.

# It need to collect static files, migrate the database and restart the server.

# The environment is passed as first argument, it can be either 'staging' or 'production'
ENVIRONMENT=$1
if [ -z "$ENVIRONMENT" ]
then
    echo "No environment specified, exiting"
    exit 1
fi

# Check if the environment is valid
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]
then
    echo "Invalid environment specified, exiting"
    exit 1
fi

export DJANGO_ENV="$ENVIRONMENT"

# Collect static files
echo "Collect static files"
./venv/bin/python manage.py collectstatic --noinput

# Migrate the database
echo "Migrate the database"
./venv/bin/python manage.py makemigrations
./venv/bin/python manage.py makemigrations drmaatic
./venv/bin/python manage.py migrate
