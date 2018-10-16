import collections
import functools
import operator

import structlog
from natsort import natsorted

from .itertools import group_by, mapv
from .utils import get_classes

log = structlog.get_logger()


def build_menu(current_version, sources, versions):
    """
    Builds a menu structure from the given sources iterable

    Sources is an iterable of dotted path strings.
    """
    data = {
        "current_version": current_version,
        "sources": dict(iter_sources(sources)),
        "versions": natsorted(versions, reverse=True),
    }

    log.info("Generated menu", version=current_version)

    return data


def iter_sources(sources):
    for source in sources:
        classes = get_classes(source, exclude=["GenericViewError"])

        def parent_module(cls):
            """
            Get the parent module for a given class.

            Given the class

                <class 'django.views.generic.detail.DetailView'>

            this will return the string "detail".
            """
            _, _, parent_name = cls.__module__.rpartition(".")
            return parent_name

        # Group classes by the module they're defined in
        classes_by_module = group_by(classes, key=parent_module)

        def reshape_classes(classes):
            """
            Reshapes the given classes list into a list of dictionaries ready
            for the front end.

            Classes is a structure like so:

                {
                    [
                        <class 'django.views.generic.dates.ArchiveIndexView'>",
                        <class 'django.views.generic.dates.DateDetailView'>,
                        ...,
                    ],
                }

            this is transformed into the structures:

                {'path': 'django.views.generic.dates', 'name': 'ArchiveIndexView'}
                {'path': 'django.views.generic.dates', 'name': 'DateDetailView'}

            """
            for cls in classes:
                yield {"name": cls.__name__, "path": cls.__module__}

        # Convert class objects to dicts ready for the front end
        classes_by_module = mapv(classes_by_module, reshape_classes)
        classes_by_module = mapv(classes_by_module, list)

        # Sort values and then keys
        sort_func = functools.partial(sorted, key=operator.itemgetter("name"))
        classes_by_module = mapv(classes_by_module, sort_func)
        classes_by_module = collections.OrderedDict(sorted(classes_by_module.items()))

        _, _, source_type = source.rpartition(".")

        yield source_type, classes_by_module
