import os

from utils import build_url, render_to_template


def build_module_page(version, module, classes):
    context = {
        'module': module,
        'classes': classes,
        'base_url': build_url(version=version, module=module),
    }
    path = os.path.join(version, module)
    render_to_template('module_list.html', context, path)


def build_klass_page(version, klass):
    context = {'klass': klass}
    path = os.path.join(version, klass.__module__, klass.__name__)
    render_to_template('klass_detail.html', context, path)
