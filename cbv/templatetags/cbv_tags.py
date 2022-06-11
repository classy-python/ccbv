import attrs
from django import template

from cbv.models import Klass, ProjectVersion


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


@register.inclusion_tag("cbv/includes/nav.html")
def nav(version, module=None, klass=None):
    other_versions = ProjectVersion.objects.filter(project=version.project).exclude(
        pk=version.pk
    )
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

    return {
        "version": version,
        "other_versions": version_switcher,
        "this_module": module,
        "this_klass": klass,
    }
