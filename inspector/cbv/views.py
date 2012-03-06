from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from cbv.models import Klass, Module, ProjectVersion, Project
from django.http import HttpResponse, HttpResponseRedirect, Http404


class HomeView(ListView):
    template_name = 'base.html'
    queryset = ProjectVersion.objects.all()  # TODO: filter for featured items.


class FuzzySingleObjectMixin(SingleObjectMixin):
    push_state_url = None

    def get_object(self, queryset=None):
        try:
            return self.get_precise_object()
        except self.model.DoesNotExist:
            try:
                obj = self.get_fuzzy_object()
                self.push_state_url = obj.get_absolute_url()
                return obj
            except self.model.DoesNotExist:
                raise Http404

    def get_context_data(self, **kwargs):
        context = super(FuzzySingleObjectMixin, self).get_context_data(**kwargs)
        context['push_state_url'] = self.push_state_url
        return context


class KlassDetailView(FuzzySingleObjectMixin, DetailView):
    model = Klass

    def get_queryset(self):
        return super(DetailView, self).get_queryset().select_related()

    def get_precise_object(self):
        return self.model.objects.filter(
            name=self.kwargs['klass'],
            module__name=self.kwargs['module'],
            module__project_version__version_number=self.kwargs['version'],
            module__project_version__project__name=self.kwargs['package'],
        ).select_related('module__project_version__project').get()

    def get_fuzzy_object(self):
        return self.model.objects.filter(
            name__iexact=self.kwargs['klass'],
            module__name__iexact=self.kwargs['module'],
            module__project_version__version_number__iexact=self.kwargs['version'],
            module__project_version__project__name__iexact=self.kwargs['package'],
        ).select_related('module__project_version__project').get()


class ModuleDetailView(FuzzySingleObjectMixin, DetailView):
    model = Module

    def get_precise_object(self, queryset=None):
        return self.model.objects.get(
            name=self.kwargs['module'],
            project_version__version_number=self.kwargs['version'],
            project_version__project__name=self.kwargs['package'],
        )

    def get_fuzzy_object(self, queryset=None):
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
