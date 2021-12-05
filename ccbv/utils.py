import importlib
import inspect
import json
import os

from first import first
from natsort import natsorted

excluded_classes = [BaseException, Exception, object]


def get_classes(source, exclude=()):
    """
    Given a dotted path source find all classes and their respective parents.

    An exclude iterable can be specified to remove potential classes from the
    output.
    """
    module = importlib.import_module(source)
    members = inspect.getmembers(module, inspect.isclass)

    classes = set()
    for _, cls in members:
        classes |= set(get_mro(cls))

    # Remove any classes specified in exclude
    classes -= set(exclude)

    # Only return classes from the given source
    classes = filter(lambda c: c.__module__.startswith(source), classes)

    return classes


def get_mro(cls):
    return filter(lambda x: x not in excluded_classes, inspect.getmro(cls))


def get_latest_version(path):
    """
    Given the output directory path, work out the latest version there.

    The home page points to the latest verison of Django we have generated docs
    for.  Since the home page will be generated after the version specific
    pages we can use the version directories in the given output path to work
    out which is the latest one.
    """
    # get items in output dir
    items = os.listdir(path)

    # get directories
    dirs = filter(lambda name: os.path.isdir(os.path.join(path, name)), items)

    # filter to ones where the first character can be converted to an int
    version_dirs = filter(lambda path: path[0].isnumeric(), dirs)

    # naturally sort the directory strings in reverse order so we can get the
    # latest version
    latest_first = natsorted(version_dirs, reverse=True)

    # get first version number
    return first(latest_first)


def load_config():
    with open("config.json") as f:
        return json.load(f)


def render(template, path, **context):
    with open(path, "w") as f:
        f.write(template.render(**context))
