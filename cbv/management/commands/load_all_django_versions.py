import glob
import os

from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    """Load the Django project fixtures and all version fixtures"""

    def handle(self, **options):
        self.stdout.write('Loading project.json')
        call_command('loaddata', 'cbv/fixtures/project.json')
        version_fixtures = glob.glob(os.path.join('cbv', 'fixtures', '*.*.*json'))
        for fixture in version_fixtures:
            self.stdout.write('Loading {}'.format(fixture))
            call_command('loaddata', fixture)
