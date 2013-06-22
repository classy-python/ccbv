from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from cbv.models import Klass, Module, ProjectVersion


class RedirectToLatestVersionView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        url_name = kwargs.pop('url_name')
        kwargs['version'] = ProjectVersion.objects.get_latest(kwargs.get('package')).version_number
        self.url = reverse_lazy(url_name, kwargs=kwargs)
        return super(RedirectToLatestVersionView, self).get_redirect_url(**kwargs)


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


class LatestKlassDetailView(FuzzySingleObjectMixin, DetailView):
    model = Klass

    def get_queryset(self):
        return super(DetailView, self).get_queryset().select_related()

    def get_precise_object(self):
        # Even if we match case-sensitively,
        # we're still going to be pushing to a new url,
        # so we'll do both lookups in get_fuzzy_object
        raise self.model.DoesNotExist

    def get_fuzzy_object(self):
        return self.model.objects.get_latest_for_name(
            klass_name=self.kwargs['klass'],
            project_name=self.kwargs['package'],
        )


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
        kwargs.update({
            'project_version': self.project_version,
            'klass_list': Klass.objects.filter(module=self.object).select_related('module__project_version', 'module__project_version__project')
        })
        return super(ModuleDetailView, self).get_context_data(**kwargs)


class VersionDetailView(ListView):
    model = Klass
    template_name = 'cbv/version_detail.html'

    def get_project_version(self, **kwargs):
        project_version = ProjectVersion.objects.filter(
            version_number__iexact=kwargs['version'],
            project__name__iexact=kwargs['package'],
        ).select_related('project').get()
        return project_version

    def get_queryset(self):
        qs = super(VersionDetailView, self).get_queryset()
        return qs.filter(module__project_version=self.project_version)

    def get_context_data(self, **kwargs):
        context = super(VersionDetailView, self).get_context_data(**kwargs)
        context['projectversion'] = self.project_version
        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project_version = self.get_project_version(**kwargs)
        except ProjectVersion.DoesNotExist:
            raise Http404
        return super(VersionDetailView, self).dispatch(request, *args, **kwargs)


class HomeView(VersionDetailView):
    template_name = 'home.html'

    def get_project_version(self, **kwargs):
        return ProjectVersion.objects.get_latest('Django')


class Sitemap(ListView):
    template_name = 'sitemap.xml'
    context_object_name = 'urlset'

    def get_queryset(self):
        latest_version = ProjectVersion.objects.get_latest('Django')
        klasses = Klass.objects.select_related('module__project_version__project')
        urls = [{
            'location': reverse('home'),
            'priority': 1.0,
        }]
        for klass in klasses:
            urls.append({
                'location': klass.get_absolute_url(),
                'priority': 0.9 if klass.module.project_version == latest_version else 0.5,
            })
        return urls

    def render_to_response(self, context, **response_kwargs):
        """
        In django 1.5+ we can replace this method with simply:
        content_type = 'application/xml'
        """
        response_kwargs['content_type'] = 'application/xml'
        return super(Sitemap, self).render_to_response(context, **response_kwargs)
