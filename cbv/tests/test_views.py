from django.test import TestCase
from django.urls import reverse

from ..views import Sitemap
from .factories import KlassFactory, ProjectVersionFactory


class SitemapTest(TestCase):
    def test_200(self):
        ProjectVersionFactory.create()
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_queryset(self):
        KlassFactory.create()
        with self.assertNumQueries(2):  # Get ProjectVersion, get Klasses.
            url_list = Sitemap().get_queryset()
        self.assertEqual(len(url_list), 2)  # 2 because 1 Klass + homepage.
