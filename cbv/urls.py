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

from django.urls import path, re_path, reverse_lazy
from django.views.generic import RedirectView

from cbv import views


urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("home"))),
    re_path(
        r"^(?P<package>[\w-]+)/$",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "version-detail"},
    ),
    re_path(
        r"^(?P<package>[\w-]+)/latest/$",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "version-detail"},
        name="latest-version-detail",
    ),
    re_path(
        r"^(?P<package>[\w-]+)/(?P<version>[^/]+)/$",
        views.VersionDetailView.as_view(),
        name="version-detail",
    ),
    re_path(
        r"^(?P<package>[\w-]+)/latest/(?P<module>[\w\.]+)/$",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "module-detail"},
        name="latest-module-detail",
    ),
    re_path(
        r"^(?P<package>[\w-]+)/(?P<version>[^/]+)/(?P<module>[\w\.]+)/$",
        views.ModuleDetailView.as_view(),
        name="module-detail",
    ),
    re_path(
        r"^(?P<package>[\w-]+)/latest/(?P<module>[\w\.]+)/(?P<klass>[\w]+)/$",
        views.RedirectToLatestVersionView.as_view(),
        {"url_name": "klass-detail"},
        name="latest-klass-detail",
    ),
    re_path(
        r"^(?P<package>[\w-]+)/(?P<version>[^/]+)/(?P<module>[\w\.]+)/(?P<klass>[\w]+)/$",
        views.KlassDetailView.as_view(),
        name="klass-detail",
    ),
]
