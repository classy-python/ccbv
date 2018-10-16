import os
import shutil
import subprocess

import click
import six
import structlog

from .utils import load_config

log = structlog.get_logger()


@click.group()
def cli():
    pass


@cli.command()
@click.argument("venvs_path")
def install(venvs_path):
    """
    Create a virtualenv for each Django version in the config.

    Each virtualenv has the specified Django version and this CCBV tool
    with its dependencies installed.
    """
    if not os.path.exists(venvs_path):
        os.makedirs(venvs_path)

    for django_version, data in six.iteritems(load_config()):
        venv_path = os.path.join(venvs_path, django_version)

        if os.path.exists(venv_path):
            shutil.rmtree(venv_path)

        subprocess.check_call(
            ["virtualenv", venv_path, "--python=python{}".format(data["version"])]
        )

        pip_path = os.path.join(venv_path, "bin", "pip")
        # eg: `pip install django~=1.3.1`
        subprocess.check_call(
            [pip_path, "install", "django~={}.1".format(django_version)]
        )
        subprocess.check_call([pip_path, "install", "-e", "."])
