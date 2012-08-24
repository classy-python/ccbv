from django.conf.urls import patterns, url

from cbv import views

urlpatterns = patterns('',
    url(r'(?P<klass>[a-zA-Z_-]+)/$', views.LatestKlassDetailView.as_view(), name='klass-detail-shortcut'),
)
