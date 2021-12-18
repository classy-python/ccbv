from pathlib import Path

import pytest
from django.test.client import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse_lazy

from ..views import Sitemap
from .factories import KlassFactory, ProjectVersionFactory


@pytest.mark.django_db
class TestSitemap:
    url = reverse_lazy("sitemap")

    def test_200(self, client: Client) -> None:
        ProjectVersionFactory.create()

        response = client.get(self.url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"

    def test_queryset(self, django_assert_num_queries: CaptureQueriesContext) -> None:
        KlassFactory.create()
        with django_assert_num_queries(2):  # Get ProjectVersion, get Klasses.

            url_list = Sitemap().get_queryset()

        assert len(url_list) == 2  # 2 because 1 Klass + homepage.

    def test_empty_content(self, client: Client) -> None:
        ProjectVersionFactory.create()

        response = client.get(self.url)

        filename = "cbv/tests/files/empty-sitemap.xml"
        assert response.content.decode() == Path(filename).read_text()
