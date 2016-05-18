import inspect
import os


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


def render(env, template_name, path, context):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.path.makedirs(directory)

    template = env.get_template(template_name + '.html')
    with open(path, 'w') as f:
        f.write(template.render(**context))
