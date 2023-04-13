import os

from django.core.wsgi import get_wsgi_application


def application(environ, start_response):
    if environ['DJANGO_ENV'] == 'development':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_dev')
    elif environ['DJANGO_ENV'] == 'staging':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_staging')
    elif environ['DJANGO_ENV'] == 'production':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_production')
    return get_wsgi_application()(environ, start_response)
