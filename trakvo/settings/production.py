from .base import *
from urllib.parse import urlparse
from decouple import config

DEBUG = False
ALLOWED_HOSTS = ['*']

db_url = urlparse(config('DATABASE_URL'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_url.path[1:],
        'USER': db_url.username,
        'PASSWORD': db_url.password,
        'HOST': db_url.hostname,
        'PORT': db_url.port,
    }
}
