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

from django.conf.urls import patterns, include, url


from cbv import views

urlpatterns = patterns('',
    url(r'^$', views.ProjectListView.as_view(), name='project-list'),
    url(r'^(?P<package>[a-zA-Z_-]+)/$', views.ProjectDetailView.as_view(), name='project-detail'),
    url(r'^(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/$', views.ModuleListView.as_view(), name='version-detail'),
    url(r'^(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/$', views.ModuleDetailView.as_view(), name='module-detail'),
    url(r'^(?P<package>[a-zA-Z_-]+)/(?P<version>[^/]+)/(?P<module>[\.A-Za-z_-]+)/(?P<klass>[A-Za-z_-]*)/$', views.KlassDetailView.as_view(), name='klass-detail'),
)
