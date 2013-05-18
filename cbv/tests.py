from django.core.urlresolvers import reverse
from django.test import TestCase
import factory

from .factories import KlassFactory, ProjectVersionFactory
from .views import Sitemap


class SitemapTest(TestCase):
    def test_200(self):
        ProjectVersionFactory.create()
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')

    def test_queryset(self):
        klass = KlassFactory.create()
        with self.assertNumQueries(2):  # Get ProjectVersion, get Klasses.
            url_list = Sitemap().get_queryset()
        self.assertEqual(len(url_list), 2)  # 2 because 1 Klass + homepage.

