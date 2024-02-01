import os
import logging

from dotenv import load_dotenv
from pathlib import Path

from environs import Env

logger = logging.getLogger(__name__)
env = Env()

# The most important thing is to be build relative path
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env(environ):
    print('Loading env variables from ' + str(BASE_DIR / 'settings' / '.env'))
    load_dotenv(BASE_DIR / 'settings' / '.env')
    print(f'Loading env variables from ' + str(BASE_DIR / 'settings' / f'.{environ["DJANGO_ENV"]}.env'))
    load_dotenv(BASE_DIR / 'settings' / f'.{environ["DJANGO_ENV"]}.env', override=True)


# The env needs to be loaded if it was not already loaded before (e.g. in docker-compose)
if 'DJANGO_ENV' in os.environ:
    load_env(os.environ)

DEBUG = env.bool('DJANGO_DEBUG', default=True)

if 'DJANGO_SECRET_KEY' in os.environ:
    SECRET_KEY = env.str('DJANGO_SECRET_KEY', None)
else:
    logger.warning('DJANGO_SECRET_KEY not found in environment variables. Using mockup value.')
    SECRET_KEY = 'not-a-secret-key'

# DRMAA library for drmaatic
os.environ["DRMAA_LIBRARY_PATH"] = env.str('DRMAA_LIBRARY_PATH', '/usr/lib/slurm-drmaa/lib/libdrmaa.so')
os.environ["SLURM_DRMAA_USE_SLURMDBD"] = env.str('SLURM_DRMAA_USE_SLURMDBD', '1')
# Set true if you want to remove the task directory when the task is deleted
REMOVE_TASK_FILES_ON_DELETE = env.bool('REMOVE_TASK_FILES_ON_DELETE', False)
# Maximum length of the parameters values, after this length an error is raised on the job submission
PARAMS_VALUES_MAX_LENGTH = env.int('PARAMS_VALUES_MAX_LENGTH', 5000)
# Maximum number of items for a paginated response
MAX_PAGE_SIZE = env.int('MAX_PAGE_SIZE', 100)

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=True)

# SUBMISSION APP FOLDERS
DRMAATIC_TASK_SCRIPT_DIR = env.path('DRMAATIC_TASK_SCRIPT_DIR', default=BASE_DIR / "tests/scripts/")
DRMAATIC_JOB_OUTPUT_DIR = env.path('DRMAATIC_JOB_OUTPUT_DIR', default=BASE_DIR / "tests/outputs/")
DRMAATIC_LOGGER_FILE_PTH = env.path('DRMAATIC_LOGGER_FILE_PTH', default=BASE_DIR / "tests/drmaatic.log")

# HTTPS flags
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', [])
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', ['*'])
X_FRAME_OPTIONS = 'ALLOWALL'
SECURE_BROWSER_XSS_FILTER = env.bool('SESSION_COOKIE_SECURE', default=False)
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

ORCID_AUTH_URL = env.str('ORCID_AUTH_URL', default='https://orcid.org/oauth/userinfo')

DRMAATIC_WS_URL = env.str('DRMAATIC_WS_URL', default='http://localhost:8000')

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
)

ONLY_JSON_APIS = env.bool('ONLY_JSON_APIS', default=False)

if not ONLY_JSON_APIS:
    DEFAULT_RENDERER_CLASSES += ('drmaatic.renderers.CustomBrowsableAPIRenderer',)

DATABASES = {
    'default': {
        'ENGINE': env.str('DATABASE_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': env.str('DATABASE_NAME', 'drmaatic'),
        'USER': env.str('DATABASE_USER', 'user'),
        'PASSWORD': env.str('DATABASE_PASSWORD', 'password'),
        'HOST': env.str('DATABASE_HOST', 'host'),
        'PORT': env.str('DATABASE_PORT', '0000'),
    }
}

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
    'drmaatic.apps.DRMAAticAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

MATOMO_TRACKING = env.bool('MATOMO_TRACKING', default=False)
MATOMO_API_TRACKING = {
    'url': env.str('MATOMO_API_URL', default=''),
    'site_id': env.int('MATOMO_SITE_ID', default=0),
}

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
TIME_ZONE = env.str('TIME_ZONE', 'UTC')
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
        "custom_format": {
            "format": "%(asctime)s - %(name)-20s - %(levelname)-7s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "custom_format",
            "filename": DRMAATIC_LOGGER_FILE_PTH,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "custom_format",
            "stream": "ext://sys.stdout"  # This sends logs to the standard output (console)
        },
    },
    'loggers': {
        'drmaatic_lib': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'drmaatic': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
