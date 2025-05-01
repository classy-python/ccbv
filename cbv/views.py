from collections import defaultdict
from collections.abc import Sequence
from typing import Any

import attrs
from django import http
from django.db.models import QuerySet
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView, View

from cbv.models import Klass, KlassAttribute, Module, ProjectVersion
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
    class Class:
        db_id: int
        docs_url: str
        docstring: str | None
        import_path: str
        name: str
        source_url: str
        url: str

    @attrs.frozen
    class Ancestor:
        name: str
        url: str
        is_direct: bool

    @attrs.frozen
    class Child:
        name: str
        url: str

    @attrs.frozen
    class Method:
        @attrs.frozen
        class MethodInstance:
            docstring: str
            code: str
            line_number: int
            class_name: str

        name: str
        kwargs: str
        namesakes: Sequence[MethodInstance]

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
        nav_builder = NavBuilder()
        version_switcher = nav_builder.make_version_switcher(
            klass.module.project_version, klass
        )
        nav = nav_builder.get_nav_data(
            klass.module.project_version, klass.module, klass
        )
        class_data = self.Class(
            db_id=klass.id,
            name=klass.name,
            docstring=klass.docstring,
            docs_url=klass.docs_url,
            import_path=klass.import_path,
            source_url=klass.get_source_url(),
            url=klass.get_absolute_url(),
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
        methods = [
            self.Method(
                name=method.name,
                kwargs=method.kwargs,
                namesakes=[
                    self.Method.MethodInstance(
                        docstring=method_instance.docstring,
                        code=method_instance.code,
                        line_number=method_instance.line_number,
                        class_name=method_instance.klass.name,
                    )
                    for method_instance in self._namesake_methods(klass, method.name)
                ],
            )
            for method in klass.get_methods()
        ]
        return {
            "all_ancestors": ancestors,
            "all_children": children,
            "attributes": self._get_prepared_attributes(klass),
            "canonical_url": self.request.build_absolute_uri(canonical_url_path),
            "class": class_data,
            "methods": methods,
            "nav": nav,
            "project": f"Django {klass.module.project_version.version_number}",
            "push_state_url": push_state_url,
            "version_switcher": version_switcher,
            "yuml_url": klass.basic_yuml_url(),
        }

    def _namesake_methods(self, parent_klass, name):
        namesakes = [m for m in parent_klass.get_methods() if m.name == name]
        assert namesakes
        # Get the methods in order of the klasses
        try:
            result = [next(m for m in namesakes if m.klass == parent_klass)]
            namesakes.pop(namesakes.index(result[0]))
        except StopIteration:
            result = []
        for klass in parent_klass.get_all_ancestors():
            # Move the namesakes from the methods to the results
            try:
                method = next(m for m in namesakes if m.klass == klass)
                namesakes.pop(namesakes.index(method))
                result.append(method)
            except StopIteration:
                pass
        assert not namesakes
        return result

    def _get_prepared_attributes(self, klass: Klass) -> QuerySet["KlassAttribute"]:
        attributes = klass.get_attributes()
        # Make a dictionary of attributes based on name
        attribute_names: dict[str, list[KlassAttribute]] = defaultdict(list)
        for attr in attributes:
            attribute_names[attr.name].append(attr)

        ancestors = klass.get_all_ancestors()

        # Sort the attributes by ancestors.
        def _key(a: KlassAttribute) -> int:
            try:
                # If ancestor, return the index (>= 0)
                return ancestors.index(a.klass)
            except ValueError:  # Raised by .index if item is not in list.
                # else a.klass == klass, so return -1
                return -1

        # Find overridden attributes
        for klass_attributes in attribute_names.values():
            # Skip if we have only one attribute.
            if len(klass_attributes) == 1:
                continue

            sorted_attrs = sorted(klass_attributes, key=_key)

            # Mark overriden KlassAttributes
            for a in sorted_attrs[1:]:
                a.overridden = True
        return attributes


class LatestKlassRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            klass = Klass.objects.get_latest_for_name(klass_name=self.kwargs["klass"])
        except Klass.DoesNotExist:
            raise http.Http404

        return klass.get_latest_version_url()


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
                    url=class_.get_absolute_url(),
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
                    url=class_.get_absolute_url(),
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
