import os
from django.core.wsgi import get_wsgi_application

if os.environ['DJANGO_ENV'] == 'development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_dev')
elif os.environ['DJANGO_ENV'] == 'staging':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_staging')
elif os.environ['DJANGO_ENV'] == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings_production')

application = get_wsgi_application()
