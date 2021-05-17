from .settings import *

DEBUG = True

STATIC_ROOT = os.path.join(BASE_DIR, '')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

ALLOWED_HOSTS = ['*']

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table_for_local_development"
    }
}

WSGI_APPLICATION = None
