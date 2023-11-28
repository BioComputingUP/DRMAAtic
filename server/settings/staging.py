import logging

from server.settings.base import *

DEBUG = True

logger = logging.getLogger(__name__)

if 'DJANGO_SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
else:
    logger.warning('DJANGO_SECRET_KEY not found in environment variables. Using mockup value.')
    SECRET_KEY = 'not-a-secret-key'

CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://dev.drmaatic.biocomputingup.it'
]

# SUBMISSION FOLDERS
SUBMISSION_SCRIPT_DIR = '/home/django/scripts-dev/'
SUBMISSION_OUTPUT_DIR = '/var/local/webservers/jobs/drmaatic-dev/'
SUBMISSION_LOGGER_PTH = '/var/local/webservers/logs/drmaatic-dev/drmaatic-dev.log'

# ORCID AUTH
ORCID_AUTH_URL = r'https://sandbox.orcid.org/oauth/userinfo'  # Production

DRMAATIC_WS_URL = 'https://dev.drmaatic.biocomputingup.it'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'drmaatic_dev',
        'USER': 'maria',
        'PASSWORD': 'password',
        'HOST': '/var/run/mysqld/mysqld.sock',
        'PORT': '3306',
    }
}

LOGGING["handlers"]["ip_request"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["handlers"]["drm"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["handlers"]["base"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["loggers"]["submission_lib"]['level'] = 'DEBUG' if DEBUG else 'INFO'
LOGGING["loggers"]["drmaatic"]['level'] = 'DEBUG' if DEBUG else 'INFO'
