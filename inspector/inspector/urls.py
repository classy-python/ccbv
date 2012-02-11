from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from cbv.views import KlassDetailView, KlassListView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='base.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^class/(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/$', KlassListView.as_view(), name='module-detail'),
	url(r'^class/(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/(?P<klass>[A-Za-z_-]*)/$', KlassDetailView.as_view(), name='klass-detail'),
)

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
