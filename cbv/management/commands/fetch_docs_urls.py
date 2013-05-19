from blessings import Terminal
from django.core.management.base import BaseCommand
from sphinx.ext.intersphinx import fetch_inventory, INVENTORY_FILENAME

from cbv.models import Klass

t = Terminal()


class Command(BaseCommand):
    args = ''
    help = 'Fetches the docs urls for CBV Classes.'
    django_doc_url = 'http://django.readthedocs.org/en/{version}'
    # these versions need to be obtained manually from RTFD website
    # do not ask me why it is `1.5.x` for Django 1.5..
    django_versions = ['1.3', '1.4', '1.5.x']

    def bless_prints(self, version, msg):
        # wish the blessings lib supports method chaining..
        a = t.blue('Django ' + version + ': ')
        z = t.green(msg)
        print a + z

    def handle(self, *args, **options):
        """
        Docs urls for Classes can differ between Django versions.
        This script sets correct urls for specific Classes using bits from
        `sphinx.ext.intersphinx` to fetch docs inventory data.
        """

        for v in self.django_versions:
            cnt = 1

            ver_url = self.django_doc_url.format(version=v)
            ver_inv_url = ver_url + '/' + INVENTORY_FILENAME

            if '.x' in v:
                v = v.split('.x')[0]
            # get flat list of CBV classes per Django version
            qs_lookups = {'module__project_version__version_number': v}
            ver_classes = Klass.objects.filter(**qs_lookups).values_list(
                'name', flat=True)
            self.bless_prints(v, 'Found {0} classes'.format(len(ver_classes)))
            self.bless_prints(v, 'Getting inventory @ {0}'.format(ver_inv_url))
            # fetch some inventory dataz
            # the arg `None` should be a Sphinx instance object..
            invdata = fetch_inventory(None, ver_url, ver_inv_url)
            for role in invdata:
                # we only want classes..
                if role == 'py:class':
                    for item in invdata[role]:
                        # ..which come from django.views
                        if 'django.views.' in item:
                            # get class name
                            inv_klass = item.split('.')[-1]
                            # save hits to db and update only required classes
                            if inv_klass in ver_classes:
                                url = invdata[role][item][2]
                                Klass.objects.filter(**qs_lookups).update(
                                    docs_url=url)
                                cnt += 1
            self.bless_prints(v, 'Updated {0} classes\n'.format(cnt))
