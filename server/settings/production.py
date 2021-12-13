from .base import *

SECRET_KEY = '67fa30081dc1d0a7f7ec0b6a3ba9739e574002f2703c124d9c1d16813a283f61a2b25ffbb69207ba9eb99e3bb10562aa06059613fe1dbde2c23116054d60769c616e40503fdba6ca2f1f1655f8c4094ba899cbb9673486e51d6de1de4e13a287ea1e9f80'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

CORS_ORIGIN_ALLOW_ALL = DEBUG

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://scheduler.biocomputingup.it']
