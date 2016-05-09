import os
import re

from django.conf import settings
from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    """Load the Django project fixtures and all version fixtures"""

    def handle(self, **options):
        fixtures_dir = os.path.join(settings.DIRNAME, 'cbv', 'fixtures')
        self.stdout.write('Loading project.json')
        call_command('loaddata', 'cbv/fixtures/project.json')
        version_fixtures = [re.match(r'((?:\d+\.){2,3}json)', filename) for filename in os.listdir(fixtures_dir)]
        for match in version_fixtures:
            try:
                fixture = match.group()
            except AttributeError:
                continue
            self.stdout.write('Loading {}'.format(fixture))
            call_command('loaddata', 'cbv/fixtures/{}'.format(fixture))
