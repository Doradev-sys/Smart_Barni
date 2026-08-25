from .base import *

DEBUG = True
SECRET_KEY = 'django-insecure-dev-key-change-in-production'
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache — LocMemCache for dev, switch to RedisCache in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'barni-cache-dev',
        'TIMEOUT': 30,
        'OPTIONS': {
            'MAX_ENTRIES': 500,
        }
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
