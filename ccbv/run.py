import argparse
import collections
import imp
import inspect
import logging
import os
import pydoc
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


BASE_VIEWS = 'views/generic/base.py'
VIEWS = 'django.views.generic'


def run():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    checkout_release(args.path, args.release)

    path = os.path.join(args.path, 'views', 'generic')
    if not os.path.exists(path):
        log.error("Couldn't find views at: {}".format(path))

    # find all classes under views.generic
    for m in filter(lambda x: '__' not in x, os.listdir(path)):
        imp.load_source(VIEWS + m.split('.')[0], os.path.join(path, m))
    members = inspect.getmembers(sys.modules[VIEWS], inspect.isclass)
    members = filter(lambda x: x[0] != 'View', members)
    modules = collections.defaultdict(list)
    for name, klass in members:
        modules[klass.__module__].append(klass)

    # Loop the imported modules.
    for module, classes in modules.items():
        # Build a detail page for the module.
        build_module_page(args.release, module, classes)
        # Build a detail page for each class in the module.
        for klass in classes:
            build_klass_page(args.release, klass)

    exit()

    try:
        structure = build(klass)
    except (ImportError, pydoc.ErrorDuringImport):
        sys.stderr.write('Could not import: {0}\n'.format(sys.argv[1]))
        sys.exit(1)

    for name, lst in structure['attributes'].items():
        for i, definition in enumerate(lst):
            a = definition['defining_class']
            structure['attributes'][name][i]['defining_class'] = a.__name__

            if isinstance(definition['object'], list):
                try:
                    s = '[{0}]'.format(', '.join([c.__name__ for c in definition['object']]))
                except AttributeError:
                    pass
                else:
                    structure['attributes'][name][i]['default'] = s
                    continue

    sorted_attributes = sorted(structure['attributes'].items(), key=lambda t: t[0])
    structure['attributes'] = collections.OrderedDict(sorted_attributes)

    sorted_methods = sorted(structure['methods'].items(), key=lambda t: t[0])
    structure['methods'] = collections.OrderedDict(sorted_methods)

    sys.exit(0)


if __name__ == '__main__':
    run()
