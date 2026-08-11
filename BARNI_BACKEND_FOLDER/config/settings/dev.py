from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = 'django-insecure-development-key-change-me'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database for development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Allow all origins for local React development
CORS_ALLOW_ALL_ORIGINS = True