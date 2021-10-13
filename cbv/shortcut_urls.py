from django.urls import re_path

from cbv import views


urlpatterns = [
    re_path(
        r"(?P<klass>[a-zA-Z_-]+)/$",
        views.LatestKlassDetailView.as_view(),
        name="klass-detail-shortcut",
    ),
]
