from django.conf.urls import url

from cbv import views

urlpatterns = [
    url(r'(?P<klass>[a-zA-Z_-]+)/$', views.LatestKlassDetailView.as_view(), name='klass-detail-shortcut'),
]
