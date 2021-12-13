import os
from pathlib import Path
from environs import Env

env = Env()

# The most important thing is to be build relative path
BASE_DIR = Path(__file__).resolve().parent.parent

# DRMAA library for submission server
os.environ.setdefault("DRMAA_LIBRARY_PATH", "/usr/lib/slurm-drmaa/libdrmaa.so")

# Group for base users, which are automatically created upon request
BASE_GROUP = 'base'

SECRET_KEY = env.str('DJANGO_SECRET_KEY', '6e4ee5f46b1606b0819d6b4d78a4d78935538a00e1badddb85db3cb9083d165a73e6be5ebd8d620621e4ecccb3f339e66d7787c5a9eb0f692d00862e5ad167113468734036b836292e3bdbb2db9cdb678960ca447a45cf52f463d25ddabdfdfe48579b45')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)

CORS_ORIGIN_ALLOW_ALL = env.bool('DJANGO_CORS_ORIGIN_ALLOW_ALL', DEBUG)

# HTTPS flags
CSRF_COOKIE_SECURE = env.bool('DJANGO_CSRF_COOKIE_SECURE', True)
SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE', True)
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', [])

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
        'rest_framework',
        'corsheaders',
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

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
        {
                'BACKEND' : 'django.template.backends.django.DjangoTemplates',
                'DIRS'    : [],
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
        'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME'  : BASE_DIR / 'db.sqlite3',
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

# Define automaic field
# NOTE https://stackoverflow.com/questions/67783120/warning-auto-created-primary-key-used-when-not-defining-a-primary-key-type-by
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
