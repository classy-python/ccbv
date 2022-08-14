from itertools import chain

from django.core import serializers
from django.core.management.base import LabelCommand

from cbv import models


class Command(LabelCommand):
    """Dump the django cbv app data for a specific version."""

    def handle_label(self, label, **options):
        querysets = (
            # There will be only one ProjectVersion, so no need for ordering.
            models.ProjectVersion.objects.filter(version_number=label),
            models.Module.objects.filter(
                project_version__version_number=label
            ).order_by("name"),
            models.Klass.objects.filter(
                module__project_version__version_number=label
            ).order_by("module__name", "name"),
            models.KlassAttribute.objects.filter(
                klass__module__project_version__version_number=label
            ).order_by("klass__module__name", "klass__name", "name"),
            models.Method.objects.filter(
                klass__module__project_version__version_number=label
            ).order_by("klass__module__name", "klass__name", "name"),
            models.Inheritance.objects.filter(
                parent__module__project_version__version_number=label
            ).order_by("child__module__name", "child__name", "order"),
        )
        objects = list(chain.from_iterable(querysets))
        for obj in objects:
            obj.pk = None
        dump = serializers.serialize(
            "json",
            objects,
            indent=1,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.stdout.write(dump)
