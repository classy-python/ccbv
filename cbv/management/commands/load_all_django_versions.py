import glob
import os

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Load the Django project fixtures and all version fixtures"""

    def handle(self, **options):
        version_fixtures = glob.glob(os.path.join("cbv", "fixtures", "*.*.*json"))
        for fixture in version_fixtures:
            self.stdout.write(f"Loading {fixture}")
            call_command("loaddata", fixture)
