# noinspection PyUnresolvedReferences
from settings import *

DEBUG = True

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
