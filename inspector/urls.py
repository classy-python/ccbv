from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView

from cbv.views import HomeView, Sitemap


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("projects/", include("cbv.urls")),
    path("sitemap.xml", Sitemap.as_view(), name="sitemap"),
    path("", include("cbv.shortcut_urls"), {"package": "Django"}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", TemplateView.as_view(template_name="500.html")),
    ]
