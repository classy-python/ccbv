import attrs

from cbv.models import Klass, Module, ProjectVersion


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


@attrs.frozen
class NavData:
    version_name: str
    version_number: str
    other_versions: list[OtherVersion]
    modules: list[ModuleData]


class NavBuilder:
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

    def get_nav_data(
        self,
        projectversion: ProjectVersion,
        module: Module | None = None,
        klass: Klass | None = None,
    ) -> NavData:
        other_versions = ProjectVersion.objects.exclude(pk=projectversion.pk)
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
                OtherVersion(
                    name=str(other_version), url=other_version.get_absolute_url()
                )
                for other_version in other_versions
            ]

        modules = [
            type(self).from_module(module=m, active_module=module, active_klass=klass)
            for m in projectversion.module_set.prefetch_related("klass_set").order_by(
                "name"
            )
        ]

        nav_data = NavData(
            version_name=str(projectversion),
            version_number=projectversion.version_number,
            other_versions=version_switcher,
            modules=modules,
        )
        return nav_data
