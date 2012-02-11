from django.conf.urls import patterns, include, url

from cbv.views import KlassDetailView, ModuleDetailView

urlpatterns = patterns('',
	url(r'^(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/$', ModuleDetailView.as_view(), name='module-detail'),
	url(r'^(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/(?P<klass>[A-Za-z_-]*)/$', KlassDetailView.as_view(), name='klass-detail'),
)
