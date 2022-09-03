from django.urls import path

from cbv import views


urlpatterns = [
    path(
        "<str:klass>/",
        views.LatestKlassDetailView.as_view(),
        name="klass-detail-shortcut",
    ),
]
