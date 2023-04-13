from server.settings import *

DEBUG = True

SECRET_KEY = 'd5rgdp(px3o9$lpk^#pr&y1s%5(w#1otyzlrv1#r+q=2@+uf&2'

CORS_ORIGIN_ALLOW_ALL = True

# HTTPS flags
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = []

ALLOWED_HOSTS = ['*']

# SUBMISSION APP FOLDERS
SUBMISSION_SCRIPT_DIR = "submission_tests/scripts/"
SUBMISSION_OUTPUT_DIR = "submission_tests/outputs/"
SUBMISSION_LOGGER_PTH = os.path.join(BASE_DIR, "logger.log")

ORCID_AUTH_URL = r'https://pub.sandbox.orcid.org/v3.0/{0:s}/record'

SUBMISSION_WS_URL = '0.0.0.0:8300'

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
