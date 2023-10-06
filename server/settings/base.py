import os
from pathlib import Path

from environs import Env

env = Env()


# The most important thing is to be build relative path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARAMS_VALUES_MAX_LENGTH = 5000

# DRMAA library for drmaatic
os.environ["DRMAA_LIBRARY_PATH"] = "/usr/lib/slurm-drmaa/lib/libdrmaa.so"
os.environ["SLURM_DRMAA_USE_SLURMDBD"] = "1"

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
    'http://localhost:4205',
    'https://ring.biocomputingup.it',
    'https://dev.proteinensemble.org',
    'https://assessment.proteinsemble.org',
    'https://biocomputingup.it',
    'https://www.biocomputingup.it',
    'https://protein.bio.unipd.it',
    'https://dev.caid.idpcentral.org',
    'https://caid.idpcentral.org',
]

ALLOWED_HOSTS = ['*']

# Set true if you want to remove the task directory when the task is deleted
REMOVE_TASK_FILES_ON_DELETE = True

MAX_PAGE_SIZE = 1000

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
    'drmaatic.renderers.CustomBrowsableAPIRenderer',
)

# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'rangefilter',  # Range filter for django admin panel
    'django_filters',  # Django filters for query parameters based filtering
    'django_extensions',
    # 'rest_framework.authtoken',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drmaatic.apps.SubmissionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'drmaatic.pagination.StandardResultsSetPagination',
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
}

dependencies = [
    ('contenttypes', '__first__'),
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Define user model
# NOTE https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#auth-custom-user
AUTH_USER_MODEL = 'drmaatic.Admin'

# Define automatic field
# NOTE https://stackoverflow.com/questions/67783120/warning-auto-created-primary-key-used-when-not-defining-a-primary-key-type-by
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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
            "filename": 'logger.log',
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
        "drm": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filters": ['shorten_name'],
            "formatter": "drm_formatter",
            "filename": 'logger.log',
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
        "base": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "drm_formatter",
            "filename": 'logger.log',
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
    },
    'filters': {
        'append_ip': {
            '()': 'drmaatic.log.IPAddressFilter'
        },
        'shorten_name': {
            '()': 'drmaatic.log.NameFilter'
        }
    },
    'loggers': {
        'submission_lib': {
            'handlers': ['drm'],
            'level': 'INFO',
            'propagate': True,
        },
        'drmaatic': {
            'handlers': ['ip_request'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['base'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
