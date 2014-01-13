import logging
import os

from jinja2 import Environment, PackageLoader


log = logging.getLogger('ccbv')


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

    # /version/django.views.generic.base
    # /version/django.views.generic.base/RedirectView
    base, head = os.path.split(path + '.html')

    build_path = os.path.join(os.getcwd(), 'build', base)

    try:
        os.makedirs(build_path)
    except OSError:
        pass

    _file = os.path.join(build_path, head)
    with open(_file, 'w') as f:
        f.write(output)
    log.debug('Built: {}'.format(_file))
