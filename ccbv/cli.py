"""
Provides top level ccbv command:

    ccbv install-versions 1.3 1.7 1.9 [--location=versions]
    ccbv generate 1.9 django.views.generic --location=versions

"""
import __builtin__
import importlib
import inspect
import os
import subprocess
import sys

import click
from jinja2 import Environment, PackageLoader

from ccbv.library import build


@click.group()
@click.option('--location', default='versions', help='Location to put version virtualenvs')
@click.pass_context
def cli(ctx, location):
    ctx.obj = location


@cli.command('install-versions')
@click.argument('versions', nargs=-1, type=float)
@click.pass_obj
def install_versions(versions_path, versions):
    """Install the given Django versions"""
    if not os.path.exists(versions_path):
        os.makedirs(versions_path)

    for version in versions:
        venv_path = os.path.join(versions_path, str(version))
        subprocess.check_call(['virtualenv', venv_path])

        pip_path = os.path.join(venv_path, 'bin', 'pip')
        args = (str(version), str(version + 0.1))
        subprocess.check_call([pip_path, 'install', 'django>={},<{}'.format(*args)])


@cli.command()
@click.argument('version')
@click.argument('sources', nargs=-1)
@click.pass_obj
def generate(versions_path, version, sources):
    # import django version
    version_path = os.path.join(versions_path, version, 'lib', 'python2.7')
    sys.path.insert(0, version_path)
    __import__('django')

    env = Environment(
        extensions=['jinja2_highlight.HighlightExtension'],
        loader=PackageLoader('ccbv', 'templates'),
    )
    template = env.get_template('klass_detail.html')

    for source in sources:
        module = importlib.import_module(source)
        members = inspect.getmembers(module, inspect.isclass)

        klasses = set()
        for name, cls in members:
            klasses |= set(filter(lambda x: x is not __builtin__.object, inspect.getmro(cls)))

        for cls in klasses:
            klass = build(cls)

            path = os.path.join('output', klass['module'])
            if not os.path.exists(path):
                os.makedirs(path)

            with open(os.path.join(path, cls.__name__ + '.html'), 'w') as f:
                f.write(template.render(klass=klass))
