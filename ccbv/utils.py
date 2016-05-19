import inspect
import os

from jinja2 import Environment, PackageLoader


excluded_classes = [
    'BaseException',
    'Exception',
    'classmethod',
    'classonlymethod',
    'dict',
    'object',
]


def get_mro(cls):
    return filter(lambda x: x.__name__ not in excluded_classes, inspect.getmro(cls))


def index(path):
    return os.path.join(path, 'index.html')


def render(template_name, path, context):
    env = Environment(
        extensions=['jinja2_highlight.HighlightExtension'],
        loader=PackageLoader('ccbv', 'templates'),
    )

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    template = env.get_template(template_name + '.html')
    with open(path, 'w') as f:
        f.write(template.render(**context))
