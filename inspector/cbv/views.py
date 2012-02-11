# Create your views here.
from django.views.generic import DetailView, ListView
from cbv.models import Klass
from django.http import HttpResponse
from pprint import pformat,pprint

class KlassDetailView(DetailView):
	model = Klass
	def get_object(self): #, request, klass, module, package, version):
		pprint(self.kwargs)
		return self.model.objects.get(
				name__iexact=self.kwargs['klass'],
				module__name__iexact=self.kwargs['module'],
				module__project_version__version_number__iexact=self.kwargs['version'],
				module__project_version__project__name__iexact=self.kwargs['package'],
				)

class KlassListView(ListView):
    model = Klass
    def get_queryset(self):
        return self.model.objects.filter(
            module__name__iexact=self.kwargs['module'],
            module__project_version__version_number__iexact=self.kwargs['version'],
            module__project_version__project__name__iexact=self.kwargs['package'],
        )
