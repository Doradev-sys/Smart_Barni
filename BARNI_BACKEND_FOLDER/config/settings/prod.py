import os
from .base import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.environ.get('DJANGO_CORS_ORIGINS', 'http://localhost:3000').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'barni'),
        'USER': os.environ.get('DB_USER', 'barni'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis cache (requires: pip install django-redis, redis-server running)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'TIMEOUT': 30,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Gunicorn bind
BIND = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')
WORKERS = int(os.environ.get('GUNICORN_WORKERS', '4'))
