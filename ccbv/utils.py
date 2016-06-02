import collections
import importlib
import inspect
import os

from jinja2 import Environment, PackageLoader
from more_itertools import chunked


excluded_classes = [
    'BaseException',
    'Exception',
    'classmethod',
    'classonlymethod',
    'dict',
    'object',
]


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
                if klass.__module__.startswith(sources):
                    yield klass


def get_mro(cls):
    return filter(lambda x: x.__name__ not in excluded_classes, inspect.getmro(cls))


def html(name):
    return '{}.html'.format(name)


def index(path):
    return os.path.join(path, 'index.html')


def map_module(module, sources):
    for source in sources:
        if module.startswith(source):
            return source

    return module


def render(template_name, path, context):
    env = Environment(
        extensions=['jinja2_highlight.HighlightExtension'],
        loader=PackageLoader('ccbv', 'templates'),
    )
    env.globals.update(chunked=chunked)

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    template = env.get_template(template_name + '.html')
    with open(path, 'w') as f:
        f.write(template.render(**context))


def setup_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ccbv.django_settings'
    from django.conf import settings
    settings.configure()

    try:
        import django
        django.setup()
    except AttributeError:  # Django < 1.7
        pass
