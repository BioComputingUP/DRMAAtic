import os
from pathlib import Path

from environs import Env

env = Env()

# The most important thing is to be build relative path
BASE_DIR = Path(__file__).resolve().parent.parent

# DRMAA library for submission server
DRMAA_LIBRARY_PATH = "/usr/lib/slurm-drmaa/lib/libdrmaa.so"
SLURM_DRMAA_USE_SLURMDBD = "1"

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
REMOVE_TASK_FILES_ON_DELETE = env.bool('REMOVE_TASK_FILES_ON_DELETE', True)

# ORCID AUTHENTICATION
ORCID_AUTH_URL = env.str('SUBMISSION_ORCID_AUTH_URL', r'https://pub.sandbox.orcid.org/v3.0/{0:s}/record')  # Development

MAX_PAGE_SIZE = env.int('MAX_PAGE_SIZE', 1000)

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
    'submission.renderers.CustomBrowsableAPIRenderer',
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
    'submission.apps.SubmissionConfig',
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
    'DEFAULT_PAGINATION_CLASS': 'submission.pagination.StandardResultsSetPagination',
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
}

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
AUTH_USER_MODEL = 'submission.Admin'

# Define automatic field
# NOTE https://stackoverflow.com/questions/67783120/warning-auto-created-primary-key-used-when-not-defining-a-primary-key-type-by
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
