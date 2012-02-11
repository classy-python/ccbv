# Create your views here.
from django.views.generic import DetailView
from cbv.models import Klass, Module
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

    def get_context_data(self, **kwargs):
        context = super(KlassDetailView, self).get_context_data(**kwargs)
        klass = context['object']
        context['ancestors'] = [r.parent for r in klass.ancestor_relationships.all()]
        return context


class KlassListView(DetailView):
    model = Module

    def get_object(self):
        return self.model.objects.get(
            name__iexact=self.kwargs['module'],
            project_version__version_number__iexact=self.kwargs['version'],
            project_version__project__name__iexact=self.kwargs['package'],
        )
