import os
from pathlib import Path

from environs import Env

env = Env()

# The most important thing is to be build relative path
BASE_DIR = Path(__file__).resolve().parent.parent

# DRMAA library for submission server
os.environ.setdefault("DRMAA_LIBRARY_PATH", "/usr/lib/slurm-drmaa/libdrmaa.so")

SECRET_KEY = env.str('DJANGO_SECRET_KEY', 'd5rgdp(px3o9$lpk^#pr&y1s%5(w#1otyzlrv1#r+q=2@+uf&2')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)
CORS_ORIGIN_ALLOW_ALL = DEBUG

CORS_ALLOWED_ORIGINS = [
        'http://localhost:4200',
        'http://localhost:4205',
        'https://ring.biocomputingup.it',
        'https://dev.proteinensemble.org',
        'https://assessment.proteinsemble.org',
        'https://biocomputingup.it',
        'https://www.biocomputingup.it',
        'https://protein.bio.unipd.it'
]

# HTTPS flags
CSRF_COOKIE_SECURE = env.bool('DJANGO_CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE', False)
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', [])

ALLOWED_HOSTS = ['*']

# SUBMISSION APP FOLDERS
SUBMISSION_SCRIPT_DIR = env.str('SUBMISSION_SCRIPT_DIR', os.path.join(BASE_DIR, "scripts/"))
SUBMISSION_OUTPUT_DIR = env.str('SUBMISSION_OUTPUT_DIR', os.path.join(BASE_DIR, "outputs/"))

SUBMISSION_LOGGER_PTH = env.str('SUBMISSION_LOGGER_PTH', os.path.join(BASE_DIR, "logger.log"))

# Set true if you want to remove the task directory when the task is deleted
REMOVE_TASK_FILES_ON_DELETE = env.bool('REMOVE_TASK_FILES_ON_DELETE', True)

# ORCID AUTHENTICATION
ORCID_AUTH_URL = env.str('SUBMISSION_ORCID_AUTH_URL', r'https://pub.sandbox.orcid.org/v3.0/{0:s}/record')  # Development

MAX_PAGE_SIZE = env.int('MAX_PAGE_SIZE', 1000)

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
        'DEFAULT_FILTER_BACKENDS' : ['django_filters.rest_framework.DjangoFilterBackend'],
        'DEFAULT_PAGINATION_CLASS': 'submission.pagination.StandardResultsSetPagination',
}

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
        {
                'BACKEND' : 'django.template.backends.django.DjangoTemplates',
                'DIRS'    : [os.path.join(BASE_DIR, 'templates')],
                'APP_DIRS': True,
                'OPTIONS' : {
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

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
        'old': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME'  : BASE_DIR / 'db.sqlite3',
        },
        'default': {
                'ENGINE'  : 'django.db.backends.mysql',
                'NAME'    : 'submission_ws',
                'USER'    : 'maria',
                'PASSWORD': 'password',
                'HOST'    : '/var/run/mysqld/mysqld.sock',
                'PORT'    : '3306',
        }
}

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
