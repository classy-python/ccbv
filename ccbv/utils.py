import importlib
import inspect
import json

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


def load_config():
    with open("config.json") as f:
        return json.load(f)
