import json

from django.db.models.query import QuerySet
from django.core.management import call_command
from django.core.management.base import LabelCommand
from django.core import serializers
from cbv import models


class Command(LabelCommand):
    """Dump the django cbv app data for a specific version."""
    def handle_label(self, label, **options):
        filtered_models = (
            (models.ProjectVersion, 'version_number'),
            (models.Module, 'project_version__version_number'),
            (models.ModuleAttribute, 'module__project_version__version_number'),
            (models.Function, 'module__project_version__version_number'),
            (models.Klass, 'module__project_version__version_number'),
            (models.KlassAttribute, 'klass__module__project_version__version_number'),
            (models.Method, 'klass__module__project_version__version_number'),
            (models.Inheritance, 'parent__module__project_version__version_number'),
        )
        objects = []
        for model, version_arg in filtered_models:
            filter_kwargs = {version_arg: label}
            result = model.objects.filter(**filter_kwargs)
            objects = objects + list(result)
        for obj in objects:
            obj.pk = None
        dump = serializers.serialize('json', objects, indent=1, use_natural_keys=True)
        self.stdout.write(dump)
