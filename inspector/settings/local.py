from __future__ import absolute_import

import os

from configurations import values

from .common import Common, DIRNAME


class Local(Common):

    # DEBUG
    DEBUG = values.BooleanValue(True)
    TEMPLATE_DEBUG = DEBUG
    # END DEBUG

    DATABASES = values.DatabaseURLValue('sqlite:///' + os.path.join(DIRNAME, 'db.sqlite'))
