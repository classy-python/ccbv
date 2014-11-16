from __future__ import absolute_import

import os

from configurations import values

from .base import Common


class Production(Common):

    # not sure why you guys do this, but I'm leaving it here to work in production.
    try:
        os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS']
        os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
        os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    except KeyError:
        # in dev this will be imported and so shouldn't
        # break the rest of the project if the environ is not there.
        pass

    # CACHING
    try:
        # See: https://github.com/rdegges/django-heroku-memcacheify
        from memcacheify import memcacheify
        CACHES = memcacheify(timeout=500)
    except ImportError:
        # simple fallback so that when this module is imported on dev
        # it won't break everything up.
        CACHES = Common.CACHES
    # END CACHING

    # SECRET KEY
    SECRET_KEY = values.SecretValue()
    # END SECRET KEY

    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('gunicorn',)

    ALLOWED_HOSTS = ('*',)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    S3_URL = 'https://{0}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
