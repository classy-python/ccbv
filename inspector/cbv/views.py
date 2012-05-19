from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from cbv.models import Klass, Module, ProjectVersion, Project


class HomeView(ListView):
    template_name = 'home.html'
    queryset = ProjectVersion.objects.all().select_related('project')  # TODO: filter for featured items.


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

    def get_context_data(self, **kwargs):
        # Get the data about this object.
        klass = self.object
        module = klass.module
        project_version = module.project_version
        project = project_version.project

        # Get the other choices for the breadcrumb dropdown.
        other_klasses = Klass.objects.filter(module=module).exclude(pk=klass.pk)
        other_modules = Module.objects.filter(project_version=project_version).exclude(pk=module.pk)
        other_versions = ProjectVersion.objects.filter(project=project).exclude(pk=project_version.pk)

        # Add them to the context
        kwargs.update({
            'other_klasses': other_klasses,
            'other_modules': other_modules,
            'other_versions': other_versions,
        })
        return super(KlassDetailView, self).get_context_data(**kwargs)


class ModuleDetailView(FuzzySingleObjectMixin, DetailView):
    model = Module

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project_version = ProjectVersion.objects.filter(
                version_number__iexact=kwargs['version'],
                project__name__iexact=kwargs['package'],
            ).select_related('project').get()
        except ProjectVersion.DoesNotExist:
            raise Http404
        return super(ModuleDetailView, self).dispatch(request, *args, **kwargs)

    def get_precise_object(self, queryset=None):
        return self.model.objects.get(
            name=self.kwargs['module'],
            project_version=self.project_version
        )

    def get_fuzzy_object(self, queryset=None):
        return self.model.objects.get(
            name__iexact=self.kwargs['module'],
            project_version__version_number__iexact=self.kwargs['version'],
            project_version__project__name__iexact=self.kwargs['package'],
        )

    def get_context_data(self, **kwargs):
        # Get the data about this object.
        module = self.object
        project_version = module.project_version
        project = project_version.project

        # Get the other choices for the breadcrumb dropdown.
        other_modules = Module.objects.filter(project_version=project_version).exclude(pk=module.pk)
        other_versions = ProjectVersion.objects.filter(project=project).exclude(pk=project_version.pk)

        # Add them to the context
        kwargs.update({
            'other_modules': other_modules,
            'other_versions': other_versions,
            'project_version': self.project_version,
            'klass_list': Klass.objects.filter(module=self.object).select_related('module__project_version', 'module__project_version__project')
        })
        return super(ModuleDetailView, self).get_context_data(**kwargs)


class ModuleListView(ListView):
    model = Module

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project_version = ProjectVersion.objects.filter(
                version_number__iexact=kwargs['version'],
                project__name__iexact=kwargs['package'],
            ).select_related('project').get()
        except ProjectVersion.DoesNotExist:
            raise Http404
        return super(ModuleListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ModuleListView, self).get_queryset()
        return qs.filter(project_version=self.project_version).select_related('project_version__project')

    def get_context_data(self, **kwargs):
        # Get the data about this object.
        project_version = self.project_version
        project = project_version.project

        # Get the other choices for the breadcrumb dropdown.
        other_versions = ProjectVersion.objects.filter(project=project).exclude(pk=project_version.pk)

        # Add them to the context
        kwargs.update({
            'other_versions': other_versions,
            'project_version': self.project_version
        })
        return super(ModuleListView, self).get_context_data(**kwargs)
