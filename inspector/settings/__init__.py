from __future__ import absolute_import

import os

# if has the $DATABASE_URL env var, then is on production
# else is local
if os.environ.get('DATABASE_URL', False):
    from .production import *
else:
    from .local import *
