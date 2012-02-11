# Create your views here.
from django.views.generic import DetailView
from cbv.models import Klass, Module, ProjectVersion, Project
from django.http import HttpResponse
from pprint import pformat,pprint

class KlassDetailView(DetailView):
    model = Klass

    def get_queryset(self):
        return super(DetailView, self).get_queryset().select_related()

    def get_object(self):
        return self.model.objects.get(
            name__iexact=self.kwargs['klass'],
            module__name__iexact=self.kwargs['module'],
            module__project_version__version_number__iexact=self.kwargs['version'],
            module__project_version__project__name__iexact=self.kwargs['package'],
        )


class ModuleDetailView(DetailView):
    model = Module

    def get_object(self):
        return self.model.objects.get(
            name__iexact=self.kwargs['module'],
            project_version__version_number__iexact=self.kwargs['version'],
            project_version__project__name__iexact=self.kwargs['package'],
        )


class VersionDetailView(DetailView):
    model = ProjectVersion

    def get_object(self):
        return self.model.objects.get(
            version_number__iexact=self.kwargs['version'],
            project__name__iexact=self.kwargs['package'],
        )

class ProjectDetailView(DetailView):
    model = Project

    def get_object(self):
        return self.model.objects.get(
            name__iexact=self.kwargs['package'],
        )
