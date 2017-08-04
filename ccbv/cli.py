"""
Provides top level ccbv command

"""
import collections
import fnmatch
import itertools
import json
import os
import subprocess
import sys
from distutils.version import StrictVersion

import click

import conf
from .library import build, is_secondary
from .utils import (get_all_descendents, get_klasses, html, index, json_dumps_default,
                    map_module, render, setup_django, sorted_dict)

DATA_DIR = 'data'
OUTPUT_DIR = 'output'


@click.group(chain=True)
@click.option('--venv-location', 'venvs_path', default='versions', help='Location to put version virtualenvs')
@click.option('--version', '-v', 'versions', multiple=True)
@click.option('--all', 'all_versions', is_flag=True)
@click.pass_context
def cli(ctx, venvs_path, versions, all_versions):
    if versions:
        if all_versions:
            click.secho('Ignoring --all-versions instruction because versions were specified', fg='red')
        unrecognised = set(versions) - set(conf.versions.keys())
        for version in unrecognised:
            click.secho("Ignoring unrecognised version '{}'".format(version), fg='red')
        versions = set(versions) & set(conf.versions.keys())

    else:
        versions = conf.versions.keys()
    versions = sorted(versions, key=StrictVersion)

    ctx.obj = dict(venvs_path=venvs_path, versions=versions)
    if len(versions) == 1:
        version = versions[0]
        ctx.obj.update(version=version)


@cli.command('install')
@click.pass_obj
def install_versions(obj):
    """Install the given Django versions"""
    if not os.path.exists(obj['venvs_path']):
        os.makedirs(obj['venvs_path'])

    for version in obj['versions']:
        venv_path = os.path.join(obj['venvs_path'], version)
        subprocess.check_call(['virtualenv', venv_path])

        pip_path = os.path.join(venv_path, 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', 'django~={}.0'.format(version)])
        subprocess.check_call([pip_path, 'install', '-e', '.'])


@cli.command()
@click.pass_obj
def inspect(obj):
    if obj.get('version'):
        inspect_version(obj['version'], obj['venvs_path'])
    else:
        for version in obj['versions']:
            try:
                subprocess.check_call(['ccbv', '-v', version, 'inspect'])
            except subprocess.CalledProcessError:
                raise click.ClickException('Failed to inspect version {}.'.format(version))
            click.echo('Version {} inspected'.format(version))

def inspect_version(version, venvs_path):
    venv_path = os.path.join(venvs_path, version)
    activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
    if not os.path.exists(activate_this):
        raise click.ClickException('Could not find virtual env for version {}. Has it been installed?'.format(version))
    execfile(activate_this, dict(__file__=activate_this))

    setup_django()

    sources = conf.versions.get(version)

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

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    data_file_path = os.path.join(DATA_DIR, version)
    with open(data_file_path, 'w') as f:
        f.write(json.dumps(data, default=json_dumps_default))


@cli.command()
@click.pass_obj
def output(obj):
    data = load_data(obj['versions'])
    for version in obj['versions']:
        sources = conf.versions.get(version)
        version_data = data[version]

        source_map = {
            'django.contrib.auth.mixins': 'Auth',
            'django.views.generic': 'Generic',
            'django.contrib.formtools.wizard.views': 'Wizard',
        }

        nav = {
            'versions': data.keys(),
            'current_version': version,
            'sources': {m: collections.defaultdict(dict) for m in sources},
        }
        for module, classes in version_data.items():
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
            'modules': version_data,
            'nav': nav,
            'version': version,
        }
        render('version_detail', index(version_path), context)

        for module, klasses in version_data.items():
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
        click.echo('Version {} pages generated'.format(version))


def load_data(versions):
    data = {}
    for version in versions:
        data_file_path = os.path.join(DATA_DIR, version)
        try:
            with open(data_file_path, 'r') as f:
                data_version, modules = json.loads(f.read()).values()
                assert data_version == version
        except IOError:
            raise click.ClickException('Failed to load data for version {}. Has it been inspected?'.format(version))
        data.update({version: modules})
        click.echo('Version {} data loaded'.format(version))
    return data


@cli.command()
@click.pass_obj
def home(obj):
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
