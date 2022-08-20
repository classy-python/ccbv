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

from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView

from cbv import views


urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("home"))),
    path(
        "<slug:package>/",
        include(
            [
                path(
                    "",
                    views.RedirectToLatestVersionView.as_view(),
                    {"url_name": "version-detail"},
                ),
                path(
                    "latest/",
                    include(
                        [
                            path(
                                "",
                                views.RedirectToLatestVersionView.as_view(),
                                {"url_name": "version-detail"},
                                name="latest-version-detail",
                            ),
                            path(
                                "<str:module>/",
                                include(
                                    [
                                        path(
                                            "",
                                            views.RedirectToLatestVersionView.as_view(),
                                            {"url_name": "module-detail"},
                                            name="latest-module-detail",
                                        ),
                                        path(
                                            "<str:klass>/",
                                            views.RedirectToLatestVersionView.as_view(),
                                            {"url_name": "klass-detail"},
                                            name="latest-klass-detail",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
                path(
                    "<str:version>/",
                    include(
                        [
                            path(
                                "",
                                views.VersionDetailView.as_view(),
                                name="version-detail",
                            ),
                            path(
                                "<str:module>/",
                                include(
                                    [
                                        path(
                                            "",
                                            views.ModuleDetailView.as_view(),
                                            name="module-detail",
                                        ),
                                        path(
                                            "<str:klass>/",
                                            views.KlassDetailView.as_view(),
                                            name="klass-detail",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
