from pathlib import Path
from typing import Protocol

import pytest
from django.test.client import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse_lazy

from .factories import KlassFactory, ProjectFactory, ProjectVersionFactory


class AssertNumQueriesFixture(Protocol):
    def __call__(self, num: int, exact: bool = True) -> CaptureQueriesContext:
        ...


@pytest.mark.django_db
class TestSitemap:
    url = reverse_lazy("sitemap")

    def test_200(self, client: Client) -> None:
        ProjectVersionFactory.create()

        response = client.get(self.url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"

    def test_queries(
        self, client: Client, django_assert_num_queries: AssertNumQueriesFixture
    ) -> None:
        KlassFactory.create()
        with django_assert_num_queries(2):  # Get ProjectVersion, get Klasses.

            client.get(self.url)

    def test_empty_content(self, client: Client) -> None:
        ProjectVersionFactory.create()

        response = client.get(self.url)

        filename = "cbv/tests/files/empty-sitemap.xml"
        assert response.content.decode() == Path(filename).read_text()

    def test_populated_content(self, client: Client) -> None:
        project = ProjectFactory(name="Django")
        KlassFactory.create(
            name="Klass",
            module__name="module.name",
            module__project_version__version_number="41.0",
            module__project_version__project=project,
        )
        KlassFactory.create(
            name="Klass",
            module__name="module.name",
            module__project_version__version_number="42.0",
            module__project_version__project=project,
        )

        response = client.get(self.url)

        filename = "cbv/tests/files/populated-sitemap.xml"
        assert response.content.decode() == Path(filename).read_text()
