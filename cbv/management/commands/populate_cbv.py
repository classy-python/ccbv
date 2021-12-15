import django
from django.conf import settings
from django.core.management.base import BaseCommand

from cbv.importer.importers import InspectCodeImporter
from cbv.importer.storages import DBStorage


class Command(BaseCommand):
    args = ""
    help = "Wipes and populates the CBV inspection models."

    def handle(self, *args, **options):
        module_paths = settings.CBV_SOURCES.keys()
        importer = InspectCodeImporter(module_paths=module_paths)
        members = importer.generate_code_data()

        DBStorage().import_project_version(
            members=members,
            project_name="Django",
            project_version=django.get_version(),
        )
