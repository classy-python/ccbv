from __future__ import absolute_import

from .base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        }

DATABASES['default'] = dj_database_url.config(default='sqlite:///' + os.path.join(DIRNAME, 'db.sqlite'))
