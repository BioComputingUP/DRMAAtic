import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SECRET_KEY'] = '3b989a58ccde0bd2c439517f0862d9576ff4535cb35d576dfc36f76fea27004d5d50e68b56cdb83fd551f40f92c6b2ad9a4185e17a3b4aa7540f86e632ebba7009f62767a236e4f5eeafeeddfb47d79ee56aaca9f109b2c6237df621c23dd13dc55ecdd8'

# SECURITY WARNING: don't run with debug turned on in production!
os.environ['DJANGO_DEBUG'] = 'True'

os.environ['DJANGO_CORS_ORIGIN_ALLOW_ALL'] = 'True'

# HTTPS flags
os.environ['DJANGO_CSRF_COOKIE_SECURE'] = 'True'
os.environ['DJANGO_SESSION_COOKIE_SECURE'] = 'True'
# os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = "['https://scheduler.biocomputingup.it']"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()

