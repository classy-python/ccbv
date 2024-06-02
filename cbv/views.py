from typing import Any

import attrs
from django import http
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView, View

from cbv.models import DjangoURLService, Klass, Module, ProjectVersion
from cbv.queries import NavBuilder


class RedirectToLatestVersionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *, url_name: str, **kwargs):
        kwargs["version"] = ProjectVersion.objects.get_latest().version_number
        self.url = reverse(url_name, kwargs=kwargs)
        return super().get_redirect_url(**kwargs)


class KlassDetailView(TemplateView):
    template_name = "cbv/klass_detail.html"

    @attrs.frozen
    class Ancestor:
        name: str
        url: str
        is_direct: bool

    @attrs.frozen
    class Child:
        name: str
        url: str

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

        latest_version = Klass.objects.select_related(
            "module__project_version"
        ).get_latest_version(module_name=klass.module.name, class_name=klass.name)
        url_service = DjangoURLService()
        canonical_url_path = url_service.class_detail(
            class_name=latest_version.name,
            module_name=latest_version.module.name,
            version_number=latest_version.module.project_version.version_number,
        )
        best_current_path = url_service.class_detail(
            class_name=klass.name,
            module_name=klass.module.name,
            version_number=klass.module.project_version.version_number,
        )
        if best_current_path != self.request.path:
            push_state_url = best_current_path
        else:
            push_state_url = None
        nav_builder = NavBuilder()
        version_switcher = nav_builder.make_version_switcher(
            klass.module.project_version, klass
        )
        nav = nav_builder.get_nav_data(
            klass.module.project_version, klass.module, klass
        )
        direct_ancestors = list(klass.get_ancestors())
        ancestors = [
            self.Ancestor(
                name=ancestor.name,
                url=ancestor.get_absolute_url(),
                is_direct=ancestor in direct_ancestors,
            )
            for ancestor in klass.get_all_ancestors()
        ]
        children = [
            self.Child(
                name=child.name,
                url=child.get_absolute_url(),
            )
            for child in klass.get_all_children()
        ]
        return {
            "all_ancestors": ancestors,
            "all_children": children,
            "attributes": klass.get_prepared_attributes(),
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "klass": klass,
            "methods": list(klass.get_methods()),
            "nav": nav,
            "project": f"Django {klass.module.project_version.version_number}",
            "push_state_url": push_state_url,
            "version_switcher": version_switcher,
            "yuml_url": klass.basic_yuml_url(),
        }


class LatestKlassRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            klass = Klass.objects.get_latest_for_name(klass_name=self.kwargs["klass"])
        except Klass.DoesNotExist:
            raise http.Http404

        return DjangoURLService().class_detail(
            class_name=klass.name,
            module_name=klass.module.name,
            version_number=klass.module.project_version.version_number,
        )


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
        url_service = DjangoURLService()
        klass_list = [
            KlassData(
                name=k.name,
                url=url_service.class_detail(
                    class_name=k.name,
                    module_name=k.module.name,
                    version_number=k.module.project_version.version_number,
                ),
            )
            for k in klasses
        ]

        latest_version = (
            Module.objects.filter(
                name=module.name,
            )
            .select_related("project_version")
            .order_by("-project_version__sortable_version_number")
            .first()
        )
        canonical_url_path = latest_version.get_absolute_url()
        nav_builder = NavBuilder()
        version_switcher = nav_builder.make_version_switcher(self.project_version)
        nav = nav_builder.get_nav_data(self.project_version, module)
        return {
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "klass_list": klass_list,
            "module_name": module.name,
            "nav": nav,
            "project": f"Django {self.project_version.version_number}",
            "push_state_url": self.push_state_url,
            "version_switcher": version_switcher,
        }


@attrs.frozen
class DjangoClassListItem:
    docstring: str
    is_secondary: bool
    name: str
    module_long_name: str
    module_name: str
    module_short_name: str
    url: str


class VersionDetailView(TemplateView):
    template_name = "cbv/version_detail.html"

    def get_context_data(self, **kwargs):
        qs = ProjectVersion.objects.filter(version_number=kwargs["version"])
        try:
            project_version = qs.get()
        except ProjectVersion.DoesNotExist:
            raise http.Http404

        nav_builder = NavBuilder()
        version_switcher = nav_builder.make_version_switcher(project_version)
        nav = nav_builder.get_nav_data(project_version)
        url_service = DjangoURLService()
        return {
            "nav": nav,
            "object_list": [
                DjangoClassListItem(
                    docstring=class_.docstring,
                    is_secondary=class_.is_secondary(),
                    name=class_.name,
                    module_long_name=class_.module.long_name,
                    module_name=class_.module.name,
                    module_short_name=class_.module.short_name,
                    url=url_service.class_detail(
                        class_name=class_.name,
                        module_name=class_.module.name,
                        version_number=project_version.version_number,
                    ),
                )
                for class_ in Klass.objects.filter(
                    module__project_version=project_version
                ).select_related("module__project_version")
            ],
            "project": f"Django {project_version.version_number}",
            "version_switcher": version_switcher,
        }


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        project_version = ProjectVersion.objects.get_latest()
        nav_builder = NavBuilder()
        version_switcher = nav_builder.make_version_switcher(project_version)
        nav = nav_builder.get_nav_data(project_version)
        url_service = DjangoURLService()
        return {
            "nav": nav,
            "object_list": [
                DjangoClassListItem(
                    docstring=class_.docstring,
                    is_secondary=class_.is_secondary(),
                    name=class_.name,
                    module_long_name=class_.module.long_name,
                    module_name=class_.module.name,
                    module_short_name=class_.module.short_name,
                    url=url_service.class_detail(
                        class_name=class_.name,
                        module_name=class_.module.name,
                        version_number=project_version.version_number,
                    ),
                )
                for class_ in Klass.objects.filter(
                    module__project_version=project_version
                ).select_related("module__project_version")
            ],
            "project": f"Django {project_version.version_number}",
            "version_switcher": version_switcher,
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

        url_service = DjangoURLService()
        urls = [{"location": reverse("home"), "priority": 1.0}]
        for klass in klasses:
            priority = 0.9 if klass.module.project_version == latest_version else 0.5
            urls.append(
                {
                    "location": url_service.class_detail(
                        class_name=klass.name,
                        module_name=klass.module.name,
                        version_number=klass.module.project_version.version_number,
                    ),
                    "priority": priority,
                }
            )
        return {"urlset": urls}


class BasicHealthcheck(View):
    """
    Minimal "up" healthcheck endpoint. Returns an empty 200 response.

    Deliberately doesn't check the state of required services such as the database
    so that a misconfigured or down DB doesn't prevent a deploy.
    """

    def get(self, request: http.HttpRequest) -> http.HttpResponse:
        return http.HttpResponse()
