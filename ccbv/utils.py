import os

from jinja2 import Environment, PackageLoader


def build_url(version=None, module=None, klass=None):
    url = '/'
    if version:
        url = url + version + '/'
    if module:
        url = url + module + '/'
    if klass:
        url = url + klass + '/'
    return url


def render_to_template(template, context, path):
    env = Environment(loader=PackageLoader('ccbv', 'templates'))
    output = env.get_template(template).render(context)

    # /1.5/django.views.generic.base.html
    # /1.5/django.views.generic.base/RedirectView.html
    base, head = os.path.split(path)

    build_path = os.path.join(os.getcwd(), 'build', base)
    print(build_path)

    try:
        os.makedirs(build_path)
    except OSError:
        pass

    _file = os.path.join(build_path, head + '.html')
    print(_file)
    with open(_file, 'w') as f:
        f.write(output)
