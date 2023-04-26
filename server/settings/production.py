from server.settings.base import *

DEBUG = False

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

CORS_ORIGIN_ALLOW_ALL = False

ALLOWED_HOSTS = ['*']

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = "https://scheduler.biocomputingup.it"

# SUBMISSION FOLDERS
SUBMISSION_SCRIPT_DIR = '/home/django/scripts'
SUBMISSION_OUTPUT_DIR = '/home/django/outputs'
SUBMISSION_LOGGER_PTH = '/home/django/logs/submission_ws.log'

# ORCID AUTHENTICATION
ORCID_AUTH_URL = r'https://orcid.org/v3.0/{0:s}/record'

SUBMISSION_WS_URL = 'https://dev.scheduler.biocomputingup.it'

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

LOGGING["handlers"]["ip_request"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["handlers"]["drm"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["handlers"]["base"]["filename"] = SUBMISSION_LOGGER_PTH
LOGGING["loggers"]["submission_lib"]['level'] = 'DEBUG' if DEBUG else 'INFO'
LOGGING["loggers"]["submission"]['level'] = 'DEBUG' if DEBUG else 'INFO'
