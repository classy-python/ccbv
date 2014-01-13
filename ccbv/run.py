import argparse
import collections
import inspect
import logging
import os
import sys

from libpydoc import build

from main import build_klass_page, build_module_page, checkout_release


logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(name)-5s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
)
log = logging.getLogger('ccbv')


parser = argparse.ArgumentParser()
parser.add_argument('path', metavar='PATH')
parser.add_argument('release', metavar='RELEASE')
args = parser.parse_args()


def run():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    checkout_release(args.path, args.release)

    views = 'django.views.generic'
    __import__(views)
    not_view = lambda x: x[0] != 'View'
    members = filter(not_view, inspect.getmembers(sys.modules[views], inspect.isclass))
    modules = collections.defaultdict(list)
    for name, klass in members:
        modules[klass.__module__].append(klass)

    for module, classes in modules.items():
        build_module_page(args.release, module, classes)
        for klass in classes:
            details = build(klass)
            path = module + '.' + klass.__name__
            build_klass_page(details, args.release, path)


if __name__ == '__main__':
    run()
