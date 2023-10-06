from server.settings.base import *

DEBUG = True

SECRET_KEY = 'y7&4Fz#&ltEL,p.%IgMU^e9pan0!;:>p@A9),qCEV<NoNw^)l0G`f&hgO"2UK)>'

CORS_ORIGIN_ALLOW_ALL = True

# HTTPS flags
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = []

ALLOWED_HOSTS = ['*']

# SUBMISSION APP FOLDERS
SUBMISSION_SCRIPT_DIR = BASE_DIR / "tests/scripts/"
SUBMISSION_OUTPUT_DIR = BASE_DIR / "tests/outputs/"
SUBMISSION_LOGGER_PTH = BASE_DIR / "logger.log"

ORCID_AUTH_URL = r'https://sandbox.orcid.org/oauth/userinfo'

DRMAATIC_WS_URL = 'http://0.0.0.0:8300'

DATABASES = {
    'old': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'drmaatic',
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
LOGGING["loggers"]["drmaatic"]['level'] = 'DEBUG' if DEBUG else 'INFO'
