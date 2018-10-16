import os
import shutil
import subprocess
import sys

import click
import six
import structlog
from jinja2 import Environment, PackageLoader

from .docs import get_docs_urls
from .library import build
from .menu import build_menu
from .utils import get_classes, load_config

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


@cli.command()
@click.argument("output_path")
def generate(output_path):
    env = Environment(
        extensions=["jinja2_highlight.HighlightExtension"],
        loader=PackageLoader("ccbv", "templates"),
    )

    os.environ["DJANGO_SETTINGS_MODULE"] = "ccbv.django_settings"

    try:
        import django

        django.setup()
    except AttributeError:  # older django versions
        pass

    template = env.get_template("klass_detail.html")

    version = sys.path[0].split("/")[-2]
    config = load_config()
    sources = config[version]["sources"]
    versions = config.keys()

    menu = build_menu(version, sources, versions)

    docs_urls = dict(get_docs_urls(version, sources))

    for source in sources:
        classes = get_classes(source, exclude=["GenericViewError"])

        for cls in classes:
            klass = build(cls, version)

            full_path = cls.__module__ + "." + cls.__name__
            klass["docs_url"] = docs_urls.get(full_path, "")

            path = os.path.join(output_path, version, klass["module"])
            if not os.path.exists(path):
                os.makedirs(path)

            with open(os.path.join(path, cls.__name__ + ".html"), "w") as f:
                f.write(template.render(klass=klass, menu=menu))

    log.info("Built all pages", version=version)
