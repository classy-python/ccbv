"""
Provides top level ccbv command:

    ccbv install-versions 1.3 1.7 1.9 [--location=versions]
    ccbv generate 1.9 django.views.generic --location=versions

"""
import os
import subprocess

import click


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
