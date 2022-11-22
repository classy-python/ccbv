from typing import Any

import attrs
from django import http
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView, View

from cbv.models import Klass, Module, ProjectVersion
from cbv.queries import get_nav_data


class RedirectToLatestVersionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *, url_name: str, **kwargs):
        kwargs["version"] = ProjectVersion.objects.get_latest().version_number
        self.url = reverse(url_name, kwargs=kwargs)
        return super().get_redirect_url(**kwargs)


class KlassDetailView(TemplateView):
    template_name = "cbv/klass_detail.html"

    def get_context_data(self, **kwargs):
        qs = Klass.objects.filter(
            name__iexact=self.kwargs["klass"],
            module__name__iexact=self.kwargs["module"],
            module__project_version__version_number=self.kwargs["version"],
        ).select_related("module__project_version")
        try:
            klass = qs.get()
        except Klass.DoesNotExist:
            raise http.Http404

        canonical_url_path = klass.get_latest_version_url()
        best_current_path = klass.get_absolute_url()
        if best_current_path != self.request.path:
            push_state_url = best_current_path
        else:
            push_state_url = None
        return {
            "all_ancestors": list(klass.get_all_ancestors()),
            "all_children": list(klass.get_all_children()),
            "attributes": klass.get_prepared_attributes(),
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "klass": klass,
            "nav": get_nav_data(klass.module.project_version, klass.module, klass),
            "methods": list(klass.get_methods()),
            "projectversion": klass.module.project_version,
            "push_state_url": push_state_url,
            "yuml_url": klass.basic_yuml_url(),
        }


class LatestKlassDetailView(TemplateView):
    template_name = "cbv/klass_detail.html"

    def get_context_data(self, **kwargs):
        try:
            klass = Klass.objects.get_latest_for_name(klass_name=self.kwargs["klass"])
        except Klass.DoesNotExist:
            raise http.Http404

        canonical_url_path = klass.get_latest_version_url()
        return {
            "all_ancestors": list(klass.get_all_ancestors()),
            "all_children": list(klass.get_all_children()),
            "attributes": klass.get_prepared_attributes(),
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "klass": klass,
            "methods": list(klass.get_methods()),
            "nav": get_nav_data(klass.module.project_version, klass.module, klass),
            "projectversion": klass.module.project_version,
            "push_state_url": klass.get_absolute_url(),
            "yuml_url": klass.basic_yuml_url(),
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
                raise http.Http404
            self.push_state_url = obj.get_absolute_url()

        return obj

    def get(self, request, *args, **kwargs):
        try:
            self.project_version = ProjectVersion.objects.filter(
                version_number=kwargs["version"]
            ).get()
        except ProjectVersion.DoesNotExist:
            raise http.Http404
        return super().get(request, *args, **kwargs)

    def get_precise_object(self, queryset=None):
        return Module.objects.get(
            name=self.kwargs["module"], project_version=self.project_version
        )

    def get_fuzzy_object(self, queryset=None):
        return Module.objects.get(
            name__iexact=self.kwargs["module"],
            project_version__version_number=self.kwargs["version"],
        )

    def get_context_data(self, **kwargs):
        module = self.get_object()
        klasses = Klass.objects.filter(module=module).select_related(
            "module__project_version"
        )
        klass_list = [KlassData(name=k.name, url=k.get_absolute_url()) for k in klasses]

        latest_version = (
            Module.objects.filter(
                name=module.name,
            )
            .select_related("project_version")
            .order_by("-project_version__sortable_version_number")
            .first()
        )
        canonical_url_path = latest_version.get_absolute_url()
        return {
            "projectversion": self.project_version,
            "klass_list": klass_list,
            "module": module,
            "nav": get_nav_data(self.project_version, module),
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "push_state_url": self.push_state_url,
        }


class VersionDetailView(TemplateView):
    template_name = "cbv/version_detail.html"

    def get_context_data(self, **kwargs):
        qs = ProjectVersion.objects.filter(version_number=kwargs["version"])
        try:
            project_version = qs.get()
        except ProjectVersion.DoesNotExist:
            raise http.Http404

        return {
            "object_list": list(
                Klass.objects.filter(
                    module__project_version=project_version
                ).select_related("module__project_version")
            ),
            "projectversion": str(project_version),
            "nav": get_nav_data(project_version),
        }


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        project_version = ProjectVersion.objects.get_latest()
        return {
            "object_list": list(
                Klass.objects.filter(
                    module__project_version=project_version
                ).select_related("module__project_version")
            ),
            "projectversion": str(project_version),
            "nav": get_nav_data(project_version),
        }


class Sitemap(TemplateView):
    content_type = "application/xml"
    template_name = "sitemap.xml"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        latest_version = ProjectVersion.objects.get_latest()
        klasses = Klass.objects.select_related("module__project_version").order_by(
            "-module__project_version__sortable_version_number",
            "module__name",
            "name",
        )

        urls = [{"location": reverse("home"), "priority": 1.0}]
        for klass in klasses:
            priority = 0.9 if klass.module.project_version == latest_version else 0.5
            urls.append({"location": klass.get_absolute_url(), "priority": priority})
        return {"urlset": urls}


class BasicHealthcheck(View):
    """
    Minimal "up" healthcheck endpoint. Returns an empty 200 response.

    Deliberately doesn't check the state of required services such as the database
    so that a misconfigured or down DB doesn't prevent a deploy.
    """

    def get(self, request: http.HttpRequest) -> http.HttpResponse:
        return http.HttpResponse()
