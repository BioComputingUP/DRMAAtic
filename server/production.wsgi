import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("ENV_NAME", "production")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.production')

application = get_wsgi_application()