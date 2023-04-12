import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SECRET_KEY'] = 'd5rgdp(px3o9$lpk^#pr&y1s%5(w#1otyzlrv1#r+q=2@+uf&2'

# SECURITY WARNING: don't run with debug turned on in production!
os.environ['DJANGO_DEBUG'] = 'False'

os.environ['DJANGO_CORS_ORIGIN_ALLOW_ALL'] = 'False'

# HTTPS flags
os.environ['DJANGO_CSRF_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_SESSION_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = "https://scheduler.biocomputingup.it"

# SUBMISSION FOLDERS
os.environ['SUBMISSION_SCRIPT_DIR'] = '/home/django/scripts'
os.environ['SUBMISSION_OUTPUT_DIR'] = '/home/django/outputs'

os.environ['SUBMISSION_LOGGER_PTH'] = '/home/django/logs/submission_ws.log'

# ORCID AUTHENTICATION
os.environ['SUBMISSION_ORCID_AUTH_URL'] = r'https://orcid.org/v3.0/{0:s}/record'  # Production

os.environ["SUBMISSION_WS_URL"] = 'https://dev.scheduler.biocomputingup.it'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'submission_ws',
        'USER': 'maria',
        'PASSWORD': 'password',
        'HOST': '/var/run/mysqld/mysqld.sock',
        'PORT': '3306',
    }
}

application = get_wsgi_application()
