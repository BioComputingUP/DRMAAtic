import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SECRET_KEY'] = '67fa30081dc1d0a7f7ec0b6a3ba9739e574002f2703c124d9c1d16813a283f61a2b25ffbb69207ba9eb99e3bb10562aa06059613fe1dbde2c23116054d60769c616e40503fdba6ca2f1f1655f8c4094ba899cbb9673486e51d6de1de4e13a287ea1e9f80'

# SECURITY WARNING: don't run with debug turned on in production!
os.environ['DJANGO_DEBUG'] = 'False'

os.environ['DJANGO_CORS_ORIGIN_ALLOW_ALL'] = 'False'

# HTTPS flags
os.environ['DJANGO_CSRF_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_SESSION_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = "['https://scheduler.biocomputingup.it']"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()
