import requests
from blessings import Terminal
from django.conf import settings
from django.core.management.base import BaseCommand
from sphinx.ext.intersphinx import fetch_inventory

from cbv.models import Klass, ProjectVersion

t = Terminal()


class Command(BaseCommand):
    args = ""
    help = "Fetches the docs urls for CBV Classes."
    # Django no longer hosts docs for < 1.7, so we only want versions that
    # are both in CCBV and at least as recent as 1.7
    django_versions = ProjectVersion.objects.exclude(
        sortable_version_number__lt="0107"
    ).values_list("version_number", flat=True)
    # Django has custom inventory file name
    inv_filename = "_objects"

    def bless_prints(self, version, msg):
        # wish the blessings lib supports method chaining..
        a = t.blue(f"Django {version}: ")
        z = t.green(msg)
        print(a + z)

    def handle(self, *args, **options):
        """
        Docs urls for Classes can differ between Django versions.
        This script sets correct urls for specific Classes using bits from
        `sphinx.ext.intersphinx` to fetch docs inventory data.
        """

        for v in self.django_versions:
            cnt = 1

            ver_url = f"https://docs.djangoproject.com/en/{v}"
            ver_inv_url = ver_url + "/" + self.inv_filename

            # get flat list of CBV classes per Django version
            qs_lookups = {"module__project_version__version_number": v}
            ver_classes = Klass.objects.filter(**qs_lookups).values_list(
                "name", flat=True
            )
            self.bless_prints(v, f"Found {len(ver_classes)} classes")
            self.bless_prints(v, f"Getting inventory @ {ver_inv_url}")
            # fetch some inventory dataz
            # the arg `r.raw` should be a Sphinx instance object..
            r = requests.get(ver_inv_url, stream=True)
            r.raise_for_status()
            invdata = fetch_inventory(r.raw, ver_url, ver_inv_url)
            # we only want classes..
            for item in invdata["py:class"]:
                # ..which come from one of our sources
                if any(source in item for source in settings.CBV_SOURCES.keys()):
                    # get class name
                    inv_klass = item.split(".")[-1]
                    # save hits to db and update only required classes
                    for vc in ver_classes:
                        if vc == inv_klass:
                            url = invdata["py:class"][item][2]
                            qs_lookups.update({"name": inv_klass})
                            Klass.objects.filter(**qs_lookups).update(docs_url=url)
                            cnt += 1
                            continue
            self.bless_prints(v, f"Updated {cnt} classes\n")
