SECRET_KEY = '952c1c3b3cedba836467afe841a051981f59b2b0d27a5ebeb3268b2992954461d2b83229e25f8b1921ae5a18293457da2228c968cc72f3700c6764d8787e608ca1ad8565d0bbb4d4a425698b101ed6820387178c8d8318b89b5e384b4100410d698be71f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ORIGIN_ALLOW_ALL = DEBUG

# HTTPS flags
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://scheduler.biocomputingup.it']
