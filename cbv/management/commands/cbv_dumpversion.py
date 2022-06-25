from django.core import serializers
from django.core.management.base import LabelCommand

from cbv import models


class Command(LabelCommand):
    """Dump the django cbv app data for a specific version."""

    def handle_label(self, label, **options):
        querysets = (
            models.ProjectVersion.objects.filter(version_number=label),
            models.Module.objects.filter(project_version__version_number=label),
            models.Klass.objects.filter(module__project_version__version_number=label),
            models.KlassAttribute.objects.filter(
                klass__module__project_version__version_number=label
            ),
            models.Method.objects.filter(
                klass__module__project_version__version_number=label
            ),
            models.Inheritance.objects.filter(
                parent__module__project_version__version_number=label
            ),
        )
        objects = []
        for queryset in querysets:
            objects = objects + list(queryset)
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
