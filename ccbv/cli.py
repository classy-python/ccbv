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
from .utils import get_classes, get_latest_version, load_config, render

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


@cli.command("classes")
@click.argument("output_path")
def build_classes(output_path):
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

    # docs_urls = dict(get_docs_urls(version, sources))

    for source in sources:
        classes = get_classes(source, exclude=["GenericViewError"])

        for cls in classes:
            klass = build(cls, version)

            # full_path = cls.__module__ + "." + cls.__name__
            # klass["docs_url"] = docs_urls.get(full_path, "")

            module_path = os.path.join(output_path, version, klass["module"])
            if not os.path.exists(module_path):
                os.makedirs(module_path)

            path = os.path.join(module_path, cls.__name__ + ".html")
            render(template, path, klass=klass, menu=menu)

    log.info("Built all pages", version=version)


@cli.command("home")
@click.argument("output_path")
def build_home(output_path):
    latest_version = get_latest_version(output_path)
    log.info("Building home page", version=latest_version)

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

    template = env.get_template("home.html")

    config = load_config()
    sources = config[latest_version]["sources"]
    versions = config.keys()
    menu = build_menu(latest_version, sources, versions)

    modules = [
        {
            "name": "Auth Mixins",
            "path": "django.contrib.auth.mixins",
            "classes": [
                {"name": "AccessMixin", "docstring": "", "is_final_form": False},
                {"name": "LoginRequiredMixin", "docstring": "", "is_final_form": False},
                {
                    "name": "PermissionRequiredMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "UserPassesTestMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
            ],
        },
        {
            "name": "Auth Views",
            "path": "django.contrib.auth.views",
            "classes": [
                {"name": "LoginView", "docstring": "", "is_final_form": True},
                {"name": "LogoutView", "docstring": "", "is_final_form": True},
                {
                    "name": "PasswordChangeDoneView",
                    "docstring": "",
                    "is_final_form": True,
                },
                {"name": "PasswordChangeView", "docstring": "", "is_final_form": True},
                {
                    "name": "PasswordContextMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "PasswordResetCompleteView",
                    "docstring": "",
                    "is_final_form": True,
                },
                {
                    "name": "PasswordResetConfirmView",
                    "docstring": "",
                    "is_final_form": True,
                },
                {
                    "name": "PasswordResetDoneView",
                    "docstring": "",
                    "is_final_form": True,
                },
                {"name": "PasswordResetView", "docstring": "", "is_final_form": True},
            ],
        },
        {
            "name": "Generic",
            "path": "django.views.generic",
            "classes": [
                {"name": "GenericViewError", "docstring": "", "is_final_form": False}
            ],
        },
        {
            "name": "Generic Base",
            "path": "django.views.generic.base",
            "classes": [
                {"name": "ContextMixin", "docstring": "", "is_final_form": False},
                {"name": "RedirectView", "docstring": "", "is_final_form": True},
                {
                    "name": "TemplateResponseMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
                {"name": "TemplateView", "docstring": "", "is_final_form": True},
                {"name": "View", "docstring": "", "is_final_form": True},
            ],
        },
        {
            "name": "Generic Dates",
            "path": "django.views.generic.dates",
            "classes": [
                {"name": "ArchiveIndexView", "docstring": "", "is_final_form": True},
                {
                    "name": "BaseArchiveIndexView",
                    "docstring": "",
                    "is_final_form": False,
                },
                {"name": "BaseDateDetailView", "docstring": "", "is_final_form": False},
                {"name": "BaseDateListView", "docstring": "", "is_final_form": False},
                {"name": "BaseDayArchiveView", "docstring": "", "is_final_form": False},
                {
                    "name": "BaseMonthArchiveView",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "BaseTodayArchiveView",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "BaseWeekArchiveView",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "BaseYearArchiveView",
                    "docstring": "",
                    "is_final_form": False,
                },
                {"name": "DateDetailView", "docstring": "", "is_final_form": True},
                {"name": "DateMixin", "docstring": "", "is_final_form": False},
                {"name": "DayArchiveView", "docstring": "", "is_final_form": True},
                {"name": "DayMixin", "docstring": "", "is_final_form": False},
                {"name": "MonthArchiveView", "docstring": "", "is_final_form": True},
                {"name": "MonthMixin", "docstring": "", "is_final_form": False},
                {"name": "TodayArchiveView", "docstring": "", "is_final_form": True},
                {"name": "WeekArchiveView", "docstring": "", "is_final_form": True},
                {"name": "WeekMixin", "docstring": "", "is_final_form": False},
                {"name": "YearArchiveView", "docstring": "", "is_final_form": True},
                {"name": "YearMixin", "docstring": "", "is_final_form": False},
            ],
        },
        {
            "name": "Generic Detail",
            "path": "django.views.generic.detail",
            "classes": [
                {"name": "BaseDetailView", "docstring": "", "is_final_form": False},
                {"name": "DetailView", "docstring": "", "is_final_form": True},
                {"name": "SingleObjectMixin", "docstring": "", "is_final_form": False},
                {
                    "name": "SingleObjectTemplateResponseMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
            ],
        },
        {
            "name": "Generic Edit",
            "path": "django.views.generic.edit",
            "classes": [
                {"name": "BaseCreateView", "docstring": "", "is_final_form": False},
                {"name": "BaseDeleteView", "docstring": "", "is_final_form": False},
                {"name": "BaseFormView", "docstring": "", "is_final_form": False},
                {"name": "BaseUpdateView", "docstring": "", "is_final_form": False},
                {"name": "CreateView", "docstring": "", "is_final_form": True},
                {"name": "DeleteView", "docstring": "", "is_final_form": True},
                {"name": "DeletionMixin", "docstring": "", "is_final_form": False},
                {"name": "FormMixin", "docstring": "", "is_final_form": False},
                {"name": "FormView", "docstring": "", "is_final_form": True},
                {"name": "ModelFormMixin", "docstring": "", "is_final_form": False},
                {"name": "ProcessFormView", "docstring": "", "is_final_form": False},
                {"name": "UpdateView", "docstring": "", "is_final_form": True},
            ],
        },
        {
            "name": "Generic List",
            "path": "django.views.generic.list",
            "classes": [
                {"name": "BaseListView", "docstring": "", "is_final_form": False},
                {"name": "ListView", "docstring": "", "is_final_form": True},
                {
                    "name": "MultipleObjectMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
                {
                    "name": "MultipleObjectTemplateResponseMixin",
                    "docstring": "",
                    "is_final_form": False,
                },
            ],
        },
    ]
    path = os.path.join(output_path, "index.html")

    render(template, path, menu=menu, version=latest_version, modules=modules)


# @cli.command()
# def testing():
#     from django.views.generic import TemplateView
#     import copy

#     version = sys.path[0].split("/")[-2]
#     print("BUILD 1")
#     data1 = build(TemplateView, version)
#     print("")
#     print("BUILD 2")
#     data2 = build2(TemplateView, version)

#     basics1 = copy.deepcopy(data1)
#     del basics1["attributes"]
#     del basics1["methods"]

#     basics2 = copy.deepcopy(data2)
#     del basics2["attributes"]
#     del basics2["methods"]

#     for k, v in six.iteritems(basics1):
#         if basics2[k] != v:
#             print("attribute '{}' differs".format(k))
#             print("basics1: {}".format(v))
#             print("basics2: {}".format(basics2[k]))
#             print("")

#     attributes1 = data1["attributes"]
#     attributes2 = data2["attributes"]
#     for k, v in six.iteritems(attributes1):
#         if attributes2[k] != v:
#             print("method '{}' differs".format(k))
#             print("attributes1: {}".format(v))
#             print("attributes2: {}".format(attributes2[k]))
#             print("")

#     methods1 = data1["methods"]
#     methods2 = data2["methods"]
#     # print(methods2)
#     for k, v in six.iteritems(methods1):
#         if methods2[k] != v:
#             print("key '{}' differs".format(k))
#             print("methods1: {}".format(v))
#             print("methods2: {}".format(methods2[k]))
#             print("")
