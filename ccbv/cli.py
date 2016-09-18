"""
Provides top level ccbv command:

    ccbv install-versions 1.3 1.7 1.9 [--location=versions]
    ccbv generate 1.9 django.views.generic --location=versions

"""
import collections
import fnmatch
import itertools
import os
import subprocess
import sys

import click

from .library import build, is_secondary
from .utils import (get_all_descendents, get_klasses, html, index, map_module,
                    render, setup_django, sorted_dict)

OUTPUT_DIR = 'output'


@click.group()
@click.option('--location', default='versions', help='Location to put version virtualenvs')
@click.pass_context
def cli(ctx, location):
    ctx.obj = location


@cli.command('install-versions')
@click.argument('versions', nargs=-1, type=str)
@click.pass_obj
def install_versions(versions_path, versions):
    """Install the given Django versions"""
    if not os.path.exists(versions_path):
        os.makedirs(versions_path)

    for version in versions:
        venv_path = os.path.join(versions_path, version)
        subprocess.check_call(['virtualenv', venv_path])

        pip_path = os.path.join(venv_path, 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', 'django~={}'.format(version)])
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

    all_klasses = set(get_klasses(sources))
    for module in {c.__module__ for c in all_klasses}:
        data['modules'][module] = collections.defaultdict(dict)

    for cls in all_klasses:
        data['modules'][cls.__module__][cls.__name__] = build(cls, version)

    # sort modules
    data['modules'] = sorted_dict(data['modules'])

    # sort classes
    for module, klasses in data['modules'].items():
        data['modules'][module] = sorted_dict(klasses)

    # add descendents to classes
    for cls, descendents in get_all_descendents(all_klasses).items():
        data['modules'][cls.__module__][cls.__name__]['descendents'] = sorted(descendents, key=lambda k: k.__name__)

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

    # loop sources (views, wizards, etc)
    for source, groups in nav['sources'].items():
        # get display name and remove dotted path name
        display_name = source_map[source]
        nav['sources'].pop(source)

        # sort classes by name
        sorted_klasses = {k: sorted_dict(v) for k, v in groups.items()}

        # sort modules by name and add to nav under display name for source
        nav['sources'][display_name] = sorted_dict(sorted_klasses)

    nav['sources'] = sorted_dict(nav['sources'])

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


@cli.command()
@click.argument('versions', nargs=-1, type=float)
@click.pass_obj
def home(versions_path, versions):
    """
    Build a home page from the current versions on disk

    The context generated here needs to match that of the base template.
    """
    versions = fnmatch.filter(os.listdir(OUTPUT_DIR), '[1-9].[1-9]')
    latest_version = max(versions)

    l = lambda: collections.defaultdict(l)  # flake8: noqa
    data = {
        'modules': {},
        'nav': {
            'latest_version': latest_version,
            'sources': collections.defaultdict(l),
        },
    }

    # get modules
    version_path = os.path.join(OUTPUT_DIR, latest_version)
    modules = filter(lambda x: not x.endswith('.html'), os.listdir(version_path))

    # get classes
    for module in modules:
        module_path = os.path.join(version_path, module)
        klasses = filter(lambda x: x != 'index.html', os.listdir(module_path))
        data['modules'][module] = klasses
        # convert klasses to dict

    # build nav
    data['nav']['versions'] = versions
    for source, modules in data['modules'].items():
        for module in itertools.ifilterfalse(is_secondary, modules):
            src = source.split('.')[2].title()
            try:
                group = source.split('.')[3].title()
            except IndexError:
                group = 'Generic'

            class_name, _ = os.path.splitext(module)
            class_name = class_name.title()
            args = (latest_version, source, module)
            data['nav']['sources'][src][group][class_name] = '/{}/{}/{}'.format(*args)

    render('home', index(OUTPUT_DIR), data)
