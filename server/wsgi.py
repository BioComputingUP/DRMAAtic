import os

import django
from django.core.handlers.wsgi import WSGIHandler


class WSGIEnvironment(WSGIHandler):

    def __call__(self, environ, start_response):

        print('DJANGO_ENV present', 'DJANGO_ENV' in environ)

        if environ['DJANGO_ENV'] == 'development':
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_dev')
        elif environ['DJANGO_ENV'] == 'staging':
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_staging')
        elif environ['DJANGO_ENV'] == 'production':
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_production')

        django.setup()
        return super(WSGIEnvironment, self).__call__(environ, start_response)


application = WSGIEnvironment()
