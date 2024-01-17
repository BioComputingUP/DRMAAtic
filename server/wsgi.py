import os

from django.core.wsgi import get_wsgi_application


# This piece of code is used to set the correct settings file, according to the environment variable DJANGO_ENV
# that is passed from the WSGI server (Apache) to the WSGI application (Django) via the SetEnv directive.
# We need to look at the environ because WSGI does not allow to pass arguments to the application.
# See https://stackoverflow.com/questions/48340719/passing-environment-variables-from-apache-via-mod-wsgi-to-use-in-django-1-11-set
def application(environ, start_response):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    os.environ.setdefault('DJANGO_ENV', environ.get('DJANGO_ENV', 'staging'))

    return get_wsgi_application()(environ, start_response)
