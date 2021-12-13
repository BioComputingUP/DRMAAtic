from .base import *
import os

print("env:", os.environ.get("ENV_NAME"))
if os.environ.get("ENV_NAME") == 'production':
    from .production import *
elif os.environ.get("ENV_NAME") == 'staging':
    from .staging import *
else:
    from .local import *
