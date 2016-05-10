from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from cbv.views import HomeView, Sitemap


admin.autodiscover()


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^projects/', include('cbv.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', Sitemap.as_view(), name='sitemap'),
    url(r'^', include('cbv.shortcut_urls'), {'package': 'Django'}),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
    ]
