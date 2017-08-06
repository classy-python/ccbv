import collections
import importlib
import inspect
import os

from jinja2 import Environment, PackageLoader
from more_itertools import chunked

import conf


excluded_classes = [
    'BaseException',
    'Exception',
    'classmethod',
    'classonlymethod',
    'dict',
    'object',
]


def long_name(module_name):
    short = short_name(module_name)
    source_name = get_source_name(module_name)
    if short.lower() == source_name.lower():
        return short
    return '{} {}'.format(source_name, short)


def get_all_descendents(klasses):
    parents_by_class = {cls: get_mro(cls)[1:] for cls in klasses}

    # reshape from child: [parents] to parent: [children]
    all_descendents = collections.defaultdict(list)
    for c, parents in parents_by_class.items():
        for parent in parents:
            all_descendents[parent].append(c)

    return all_descendents


def get_klasses(sources):
    for source in sources:
        module = importlib.import_module(source)
        members = inspect.getmembers(module, inspect.isclass)

        for name, cls in members:
            for klass in get_mro(cls):
                if klass.__module__.startswith(source):
                    yield klass


def get_mro(cls):
    return filter(lambda x: x.__name__ not in excluded_classes, inspect.getmro(cls))


def get_source_name(module_name):
    while module_name:
        try:
            return conf.source_names[module_name]
        except KeyError:
            module_name = '.'.join(module_name.split('.')[:-1])


def html(name):
    return '{}.html'.format(name)


def index(path):
    return os.path.join(path, 'index.html')


def json_dumps_default(obj):
    try:
        return dict(name=obj.__name__, module=obj.__module__)
    except:
        pass
    if type(obj) == set:
        return list(obj)
    if obj.__class__.__name__ == 'LazyAttribute':
        return str(obj)
    try:
        return str(obj)
    except:
        raise TypeError('Cannot serialize {}'.format(type(obj)))


def map_module(module, sources):
    for source in sources:
        if module.startswith(source):
            return source

    return module


def render(template_name, path, context):
    env = Environment(
        extensions=['jinja2_highlight.HighlightExtension', 'jinja2.ext.with_'],
        loader=PackageLoader('ccbv', 'templates'),
    )
    env.globals.update(chunked=chunked, long_name=long_name)

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    template = env.get_template(template_name + '.html')
    with open(path, 'w') as f:
        f.write(template.render(**context))


def setup_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ccbv.django_settings'
    from django.conf import settings

    try:
        import django
        django.setup()
    except AttributeError:  # Django < 1.7
        pass


def short_name(module_name):
    return module_name.split('.')[-1]


def sorted_dict(thing):
    return collections.OrderedDict(sorted(thing.items()))
