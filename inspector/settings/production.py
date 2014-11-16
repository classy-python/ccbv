from __future__ import absolute_import

from .base import *

os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS']
os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']

CACHES = {
            'default': {
                'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
                'LOCATION': os.environ['MEMCACHIER_SERVERS'],
                'TIMEOUT': 500,
                'BINARY': True,
            }
        }


INSTALLED_APPS = INSTALLED_APPS + ('gunicorn',)

ALLOWED_HOSTS = ('*',)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'https://{0}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
