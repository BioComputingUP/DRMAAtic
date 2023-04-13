from server.settings import *

DEBUG = True

SECRET_KEY = 'd5rgdp(px3o9$lpk^#pr&y1s%5(w#1otyzlrv1#r+q=2@+uf&2'

CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://dev.scheduler.biocomputingup.it'
]

# SUBMISSION FOLDERS
SUBMISSION_SCRIPT_DIR = '/home/django/scripts'
SUBMISSION_OUTPUT_DIR = '/var/local/webservers/jobs/scheduler-dev/outputs'
SUBMISSION_LOGGER_PTH = '/var/local/webservers/logs/scheduler-dev/scheduler-dev.log'

# ORCID AUTH
ORCID_AUTH_URL = r'https://orcid.org/v3.0/{0:s}/record'  # Production

SUBMISSION_WS_URL = 'https://dev.scheduler.biocomputingup.it'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'submission_ws_dev',
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
