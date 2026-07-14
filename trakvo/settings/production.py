import dj_database_url
from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')
CSRF_TRUSTED_ORIGINS = [url.strip() for url in CSRF_TRUSTED_ORIGINS if url.strip()]

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# Ensure HTTPS in production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
