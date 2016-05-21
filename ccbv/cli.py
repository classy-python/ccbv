"""
Provides top level ccbv command:

    ccbv install-versions 1.3 1.7 1.9 [--location=versions]
    ccbv generate 1.9 django.views.generic --location=versions

"""
import collections
import importlib
import inspect
import os
import subprocess
import sys
from collections import OrderedDict

import click

from .library import build
from .utils import get_mro, html, index, map_module, render, setup_django

OUTPUT_DIR = 'output'


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
        subprocess.check_call([pip_path, 'install', '-e', '.'])


@cli.command()
@click.argument('version')
@click.argument('sources', nargs=-1)
@click.pass_obj
def generate(versions_path, version, sources):


    setup_django()

    # DATA GENERATION
    data = {
        'modules': {},
        'version': version,
    }

    for source in sources:
        module = importlib.import_module(source)
        members = inspect.getmembers(module, inspect.isclass)

        klasses = set()
        for name, cls in members:
            klasses |= set(get_mro(cls))

        for module in {c.__module__ for c in klasses}:
            data['modules'][module] = collections.defaultdict(dict)

        for cls in klasses:
            data['modules'][cls.__module__][cls.__name__] = build(cls, version)
        # TODO: sort by class name

        parents_by_class = {cls: get_mro(cls)[1:] for cls in klasses}

        # reshape from child: [parents] to parent: [children]
        all_descendents = collections.defaultdict(list)
        for c, parents in parents_by_class.items():
            for parent in parents:
                all_descendents[parent].append(c)

        # add descendents to classes
        for cls, descendents in all_descendents.items():
            data['modules'][cls.__module__][cls.__name__]['descendents'] = sorted(descendents, key=lambda k: (k.__module__, k.__name__))

    source_map = {
        'django.contrib.auth.mixins': 'Auth',
        'django.views.generic': 'Generic',
        'django.contrib.formtools.wizard.views': 'Wizard',
    }

    nav = {
        'versions': [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],  # TODO: get from cli
        'current_version': version,
        'sources': {m: collections.defaultdict(dict) for m in sources},
    }
    for module, classes in data['modules'].items():
        for cls, info in classes.items():
            source = map_module(info['module'], sources)
            if source not in sources:
                continue

            _, _, head = info['module'].rpartition('.')
            nav['sources'][source][head][cls] = os.path.join(info['module'], html(cls))

    for source, groups in nav['sources'].items():
        display_name = source_map[source]
        nav['sources'].pop(source)
        nav['sources'][display_name] = {k: OrderedDict(sorted(v.items())) for k, v in groups.items()}

    nav['sources'] = OrderedDict(sorted(nav['sources'].items()))

    # TEMPLATE GENERATION
    version_path = os.path.join(OUTPUT_DIR, version)

    context = {
        'modules': data['modules'],
        'nav': nav,
        'version': version,
    }
    render('version_detail', index(version_path), context)

    for module, klasses in data['modules'].items():
        module_path = os.path.join(version_path, module)

        context = {
            'klasses': klasses,
            'module_name': module,
            'nav': nav,
        }
        render('module_detail', index(module_path), context)

        for name, klass in klasses.items():
            context = {
                'klass': klass,
                'klass_name': name,
                'nav': nav,
            }
            path = os.path.join(module_path, name + '.html')
            render('klass_detail', path, context)
