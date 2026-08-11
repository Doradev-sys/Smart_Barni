from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Use environment variables for secrets in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Production Database (e.g., PostgreSQL configuration placeholder)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Update to postgresql if needed
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Restrict CORS to specific production front-end domains
CORS_ALLOWED_ORIGINS = [
    # "https://your-frontend-domain.com",
]