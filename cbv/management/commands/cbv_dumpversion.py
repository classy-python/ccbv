from django.core.management import call_command
from django.core.management.commands import LabelCommand


class Command(LabelCommand):
    def handle_label(self, label, **options):
        # Because django will use the default manager of each model, we
        # monkeypatch the manager to filter by our label before calling
        # the dumpdata command to dump only the subset of data we want.

        # Set the 

        # Call the dumpdata command.
        call_command('dumpdata', 'cbv')
