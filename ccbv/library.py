import collections
import inspect
import operator
import pydoc

import six

from first import first
from more_itertools import pairwise

from .itertools import group_by, mapv
from .utils import get_mro


def build(thing, version):
    """Build a dictionary mapping of a class."""
    klass, name = pydoc.resolve(thing, forceload=0)
    mro = list(reversed(list(get_mro(klass))))
    _, start_line = inspect.getsourcelines(klass)

    source_url = "https://github.com/django/django/blob/{version}/{module_path}.py#L{line}".format(
        line=start_line, module_path=klass.__module__.replace(".", "/"), version=version
    )

    all_attributes = sorted(build_attributes(mro), key=operator.itemgetter(0))
    attributes = filter_attributes(all_attributes)

    methods = sorted(build_methods(mro), key=operator.itemgetter(0))
    methods = collections.OrderedDict(methods)
    methods = mapv(methods, lambda m: [m])
    # TODO: compare against methods for build1
    # TODO: needs a test!

    return {
        "ancestors": collections.OrderedDict(
            [(k.__name__, k.__module__) for k in mro[:-1]]
        ),
        "attributes": attributes,
        "docstring": pydoc.getdoc(klass),
        "source_url": source_url,
        "methods": methods,
        "module": klass.__module__,
        "name": name,
        "parents": inspect.getclasstree([klass])[-1][0][1],
        "properties": [],
    }


def build_attributes(classes):
    """
    Build (name, data) pairs for each attribute on each given class.

    This function does no filtering of where attributes are originally defined
    by design.
    """
    for cls in classes:
        attributes = (
            (name, attr)
            for name, attr in get_members(cls)
            if not (inspect.ismethod(attr) or inspect.isfunction(attr))
        )

        for name, obj in attributes:
            # convert attributes for display
            # TODO: Move to the template
            if inspect.isclass(obj):
                obj = obj.__name__
            elif isinstance(obj, six.string_types):
                obj = "'{}'".format(obj)

            yield name, {"value": obj, "defining_class": cls}


def build_method(cls, method):
    """Build the datastructure for a single method."""
    # Get source line details
    lines, start_line = inspect.getsourcelines(method)
    whitespace = len(lines[0]) - len(lines[0].lstrip())
    for i, line in enumerate(lines):
        lines[i] = line[whitespace:]
    code = "".join(lines).strip()

    # Get the method arguments
    args, varargs, keywords, defaults = get_method_argspec(method)
    arguments = inspect.formatargspec(
        args, varargs=varargs, varkw=keywords, defaults=defaults
    )

    return {
        "docstring": pydoc.getdoc(method),
        "defining_class": cls,
        "arguments": arguments,
        "code": code,
        "lines": {"start": start_line, "total": len(lines)},
        "file": inspect.getsourcefile(method),
    }


def build_methods(classes):
    """
    Build method data structure for each class in the iterable.
    """
    for cls in classes:
        methods = (
            (name, method)
            for name, method in get_members(cls)
            if inspect.ismethod(method) or inspect.isfunction(method)
        )

        for name, method in methods:
            yield name, build_method(cls, method)


def filter_attributes(all_attributes):
    # TODO: needs a test!
    attributes = group_by(all_attributes, key=operator.itemgetter(0))

    def hoist_values(structures):
        """
        Remove attribute name keys now we've grouped by them.

        `structures` is an iterable of:

            (attribute_name, data)

        Where we only want the `data` structures.
        """
        for item in structures:
            yield item[1]

    attributes = mapv(attributes, hoist_values)

    def remove_duplicate_attributes(structures):
        """
        Remove duplicate attribute structures from the given iterable.

        `structures` is an iterable of all versions of a single attribute on a
        single class.  The `build_attributes` method actively doesn't filter
        these since it has no cross-class knowledge.

        We always return the first item since that's the earliest version of
        the attribute.  Next we pair up the items in the iterable giving us an
        iterable of pair windows.  We use this to check each "child" attribute
        value is different to the "parent" one.
        """
        structures = list(structures)
        yield first(structures)

        for pair in pairwise(structures):
            parent, child = pair
            # FIXME: lazy attributes get evaluated in this comparison, fix that
            if child["value"] != parent["value"]:
                yield child

    attributes = mapv(attributes, remove_duplicate_attributes)
    attributes = mapv(attributes, list)
    attributes = collections.OrderedDict(attributes)

    return attributes


def get_members(cls):
    """
    Get members for the given class.

    Filters out double underscore methods but keeps __init__.
    """
    return filter(
        lambda m: m[0] == "__init__" or not m[0].startswith("__"),
        inspect.getmembers(cls),
    )


def get_method_argspec(method):
    """
    Given a method find the argument spec for it.

    Python 2's inspect.getargspec does not handle keyword only args or
    annotations so we fall back to inspect.getfullargspec (3.0+).
    """
    try:
        return inspect.getargspec(method)
    except ValueError:  # keyword only params or annotations
        spec = inspect.getfullargspec(method)
        return spec.args, spec.varargs, spec.varkw, spec.defaults
