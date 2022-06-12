from typing import Any

import attrs
from django.http import Http404
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, TemplateView

from cbv.models import Klass, Module, ProjectVersion


class RedirectToLatestVersionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *, package: str, url_name: str, **kwargs):
        kwargs["version"] = ProjectVersion.objects.get_latest(package).version_number
        self.url = reverse(url_name, kwargs={"package": package, **kwargs})
        return super().get_redirect_url(**kwargs)


class KlassDetailView(DetailView):
    model = Klass
    template_name = "cbv/klass_detail.html"
    push_state_url = None

    def get_object(self, queryset=None):
        try:
            obj = self.get_precise_object()
        except self.model.DoesNotExist:
            try:
                obj = self.get_fuzzy_object()
            except self.model.DoesNotExist:
                raise Http404
            self.push_state_url = obj.get_absolute_url()

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canonical_url_path = self.object.get_latest_version_url()
        context["canonical_url"] = self.request.build_absolute_uri(canonical_url_path)
        context["push_state_url"] = self.push_state_url
        return context

    def get_precise_object(self):
        return (
            self.model.objects.filter(
                name=self.kwargs["klass"],
                module__name=self.kwargs["module"],
                module__project_version__version_number=self.kwargs["version"],
                module__project_version__project__name=self.kwargs["package"],
            )
            .select_related("module__project_version__project")
            .get()
        )

    def get_fuzzy_object(self):
        return (
            self.model.objects.filter(
                name__iexact=self.kwargs["klass"],
                module__name__iexact=self.kwargs["module"],
                module__project_version__version_number__iexact=self.kwargs["version"],
                module__project_version__project__name__iexact=self.kwargs["package"],
            )
            .select_related("module__project_version__project")
            .get()
        )


class LatestKlassDetailView(TemplateView):
    push_state_url = None
    template_name = "cbv/klass_detail.html"

    def get_context_data(self, **kwargs):
        try:
            klass = Klass.objects.get_latest_for_name(
                klass_name=self.kwargs["klass"],
                project_name=self.kwargs["package"],
            )
        except Klass.DoesNotExist:
            raise Http404

        canonical_url_path = klass.get_latest_version_url()
        return {
            "klass": klass,
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "push_state_url": klass.get_absolute_url(),
        }


@attrs.frozen
class KlassData:
    name: str
    url: str


class ModuleDetailView(TemplateView):
    template_name = "cbv/module_detail.html"
    push_state_url = None

    def get_object(self, queryset=None):
        try:
            obj = self.get_precise_object()
        except Module.DoesNotExist:
            try:
                obj = self.get_fuzzy_object()
            except Module.DoesNotExist:
                raise Http404
            self.push_state_url = obj.get_absolute_url()

        return obj

    def get(self, request, *args, **kwargs):
        try:
            self.project_version = (
                ProjectVersion.objects.filter(
                    version_number__iexact=kwargs["version"],
                    project__name__iexact=kwargs["package"],
                )
                .select_related("project")
                .get()
            )
        except ProjectVersion.DoesNotExist:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_precise_object(self, queryset=None):
        return Module.objects.get(
            name=self.kwargs["module"], project_version=self.project_version
        )

    def get_fuzzy_object(self, queryset=None):
        return Module.objects.get(
            name__iexact=self.kwargs["module"],
            project_version__version_number__iexact=self.kwargs["version"],
            project_version__project__name__iexact=self.kwargs["package"],
        )

    def get_context_data(self, **kwargs):
        module = self.get_object()
        klasses = Klass.objects.filter(module=module).select_related(
            "module__project_version", "module__project_version__project"
        )
        klass_list = [KlassData(name=k.name, url=k.get_absolute_url()) for k in klasses]

        latest_version = (
            Module.objects.filter(
                project_version__project=self.project_version.project,
                name=module.name,
            )
            .select_related("project_version__project")
            .order_by("-project_version__sortable_version_number")
            .first()
        )
        canonical_url_path = latest_version.get_absolute_url()
        return {
            "project_version": self.project_version,
            "klass_list": klass_list,
            "module": module,
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "push_state_url": self.push_state_url,
        }


class VersionDetailView(TemplateView):
    template_name = "cbv/version_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            self.project_version = self.get_project_version(**kwargs)
        except ProjectVersion.DoesNotExist:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_project_version(self, **kwargs):
        project_version = (
            ProjectVersion.objects.filter(
                version_number__iexact=kwargs["version"],
                project__name__iexact=kwargs["package"],
            )
            .select_related("project")
            .get()
        )
        return project_version

    def get_context_data(self, **kwargs):
        return {
            "object_list": Klass.objects.filter(
                module__project_version=self.project_version
            ).select_related("module__project_version__project"),
            "projectversion": self.project_version,
        }


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        project_version = ProjectVersion.objects.get_latest("Django")
        return {
            "object_list": Klass.objects.filter(
                module__project_version=project_version
            ).select_related("module__project_version__project"),
            "projectversion": project_version,
        }


class Sitemap(TemplateView):
    content_type = "application/xml"
    template_name = "sitemap.xml"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        latest_version = ProjectVersion.objects.get_latest("Django")
        klasses = Klass.objects.select_related(
            "module__project_version__project"
        ).order_by(
            "module__project_version__project__name",
            "-module__project_version__sortable_version_number",
            "module__name",
            "name",
        )

        urls = [{"location": reverse("home"), "priority": 1.0}]
        for klass in klasses:
            priority = 0.9 if klass.module.project_version == latest_version else 0.5
            urls.append({"location": klass.get_absolute_url(), "priority": priority})
        return {"urlset": urls}
