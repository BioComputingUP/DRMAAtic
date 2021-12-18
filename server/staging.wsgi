import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SECRET_KEY'] = 'f81998978f1ff1aa6ead635a63b9070df70978947686751d9b53eeff43ee7e47f9e592e65239a09142946dc281c6e90550d04d54512043f4c4860a04ba1360e74830f8b67a362eb6b20babf3ef5c15913729d6d9a635864e1b76954504bb9ad92e733e15'

# SECURITY WARNING: don't run with debug turned on in production!
os.environ['DJANGO_DEBUG'] = 'True'

os.environ['DJANGO_CORS_ORIGIN_ALLOW_ALL'] = 'True'

# HTTPS flags
os.environ['DJANGO_CSRF_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_SESSION_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = "['https://dev.scheduler.biocomputingup.it']"

# SUBMISSION FOLDERS
os.environ['SUBMISSION_SCRIPT_DIR'] = '/home/django/scripts'
os.environ['SUBMISSION_OUTPUT_DIR'] = '/home/django/outputs'

# ORCID AUTH
os.environ['ORCID_AUTH_URL'] = r'https://orcid.org/v3.0/{0:s}/record'  # Production

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()
