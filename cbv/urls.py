"""
URL variations:
project
project/version
project/version/module
project/version/module/class

e.g.
django
django/1.41a
django/1.41a/core
django/1.41a/core/DjangoRuntimeWarning
"""

from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from cbv import views


urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("home"))),
    path(
        "Django/",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "version-detail"},
    ),
    path(
        "Django/latest/",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "version-detail"},
        name="latest-version-detail",
    ),
    path(
        "Django/<str:version>/",
        views.VersionDetailView.as_view(),
        name="version-detail",
    ),
    path(
        "Django/latest/<str:module>/",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "module-detail"},
        name="latest-module-detail",
    ),
    path(
        "Django/<str:version>/<str:module>/",
        views.ModuleDetailView.as_view(),
        name="module-detail",
    ),
    path(
        "Django/latest/<str:module>/<str:klass>/",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "klass-detail"},
        name="latest-klass-detail",
    ),
    path(
        "Django/<str:version>/<str:module>/<str:klass>/",
        views.KlassDetailView.as_view(),
        name="klass-detail",
    ),
]
