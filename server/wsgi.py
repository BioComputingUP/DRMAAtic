import os

from django.core.wsgi import get_wsgi_application


# This piece of code is used to set the correct settings file, according to the environment variable DJANGO_ENV
# that is passed from the WSGI server (Apache) to the WSGI application (Django) via the SetEnv directive.
# We need to look at the environ because WSGI does not allow to pass arguments to the application.
# See https://stackoverflow.com/questions/48340719/passing-environment-variables-from-apache-via-mod-wsgi-to-use-in-django-1-11-set
def application(environ, start_response):
    if 'DJANGO_ENV' not in environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_dev')
    elif environ['DJANGO_ENV'] == 'development':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_dev')
    elif environ['DJANGO_ENV'] == 'staging':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_staging')
    elif environ['DJANGO_ENV'] == 'production':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_production')
    return get_wsgi_application()(environ, start_response)
