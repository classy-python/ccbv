import attrs
from django import template

from cbv.models import Klass, Module, ProjectVersion


register = template.Library()


@register.filter
def namesake_methods(parent_klass, name):
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


@attrs.frozen
class OtherVersion:
    name: str
    url: str


@attrs.frozen
class ModuleData:
    @attrs.frozen
    class KlassData:
        name: str
        url: str
        active: bool

    source_name: str
    short_name: str
    classes: list[KlassData]
    active: bool

    @classmethod
    def from_module(
        cls, module: Module, active_module: Module | None, active_klass: Klass | None
    ) -> "ModuleData":
        return ModuleData(
            source_name=module.source_name(),
            short_name=module.short_name(),
            classes=[
                ModuleData.KlassData(
                    name=klass.name,
                    url=klass.get_absolute_url(),
                    active=klass == active_klass,
                )
                for klass in module.klass_set.all()
            ],
            active=module == active_module,
        )


@register.inclusion_tag("cbv/includes/nav.html")
def nav(version, module=None, klass=None):
    other_versions = ProjectVersion.objects.filter(
        project_id=version.project_id
    ).exclude(pk=version.pk)
    if klass:
        other_versions_of_klass = Klass.objects.filter(
            name=klass.name,
            module__project_version__in=other_versions,
        )
        other_versions_of_klass_dict = {
            x.module.project_version: x for x in other_versions_of_klass
        }
        version_switcher = []
        for other_version in other_versions:
            try:
                other_klass = other_versions_of_klass_dict[other_version]
            except KeyError:
                url = other_version.get_absolute_url()
            else:
                url = other_klass.get_absolute_url()

            version_switcher.append(OtherVersion(name=str(other_version), url=url))
    else:
        version_switcher = [
            OtherVersion(name=str(other_version), url=other_version.get_absolute_url())
            for other_version in other_versions
        ]

    modules = [
        ModuleData.from_module(module=m, active_module=module, active_klass=klass)
        for m in version.module_set.prefetch_related("klass_set").order_by("name")
    ]

    return {
        "version": version,
        "other_versions": version_switcher,
        "modules": modules,
    }
