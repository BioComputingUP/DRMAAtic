# noinspection PyUnresolvedReferences
from settings import *

DEBUG = False

SECRET_KEY = 'd5rgdp(px3o9$lpk^#pr&y1s%5(w#1otyzlrv1#r+q=2@+uf&2'

CORS_ORIGIN_ALLOW_ALL = False

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = "https://scheduler.biocomputingup.it"

# SUBMISSION FOLDERS
SUBMISSION_SCRIPT_DIR = '/home/django/scripts'
SUBMISSION_OUTPUT_DIR = '/home/django/outputs'
SUBMISSION_LOGGER_PTH = '/home/django/logs/submission_ws.log'

# ORCID AUTHENTICATION
SUBMISSION_ORCID_AUTH_URL = r'https://orcid.org/v3.0/{0:s}/record'

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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "request_formatter": {
            "format": "%(asctime)s - %(name)-20s - %(levelname)-7s - %(ip)-15s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "drm_formatter": {
            "format": "%(asctime)s - %(name)-20s - %(levelname)-7s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "ip_request": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "request_formatter",
            'filters': ['append_ip', 'shorten_name'],
            "filename": SUBMISSION_LOGGER_PTH,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
        "drm": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filters": ['shorten_name'],
            "formatter": "drm_formatter",
            "filename": SUBMISSION_LOGGER_PTH,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
        "base": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "drm_formatter",
            "filename": SUBMISSION_LOGGER_PTH,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
    },
    'filters': {
        'append_ip': {
            '()': 'submission.log.IPAddressFilter'
        },
        'shorten_name': {
            '()': 'submission.log.NameFilter'
        }
    },
    'loggers': {
        'submission_lib': {
            'handlers': ['drm'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': True,
        },
        'submission': {
            'handlers': ['ip_request'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': True,
        },
        'django': {
            'handlers': ['base'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
