import attrs

from cbv import models


@attrs.frozen
class NavData:
    version_name: str
    other_versions: list["OtherVersion"]
    modules: list["Module"]

    @attrs.frozen
    class OtherVersion:
        name: str
        url: str

    @attrs.frozen
    class Klass:
        name: str
        url: str
        active: bool

    @attrs.frozen
    class Module:
        source_name: str
        short_name: str
        classes: list["NavData.Klass"]
        active: bool


class NavBuilder:
    def _to_module_data(
        self,
        module: models.Module,
        active_module: models.Module | None,
        active_klass: models.Klass | None,
    ) -> "NavData.Module":
        return NavData.Module(
            source_name=module.source_name(),
            short_name=module.short_name(),
            classes=[
                NavData.Klass(
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
        projectversion: models.ProjectVersion,
        module: models.Module | None = None,
        klass: models.Klass | None = None,
    ) -> NavData:
        other_versions = models.ProjectVersion.objects.exclude(pk=projectversion.pk)
        if klass:
            other_versions_of_klass = models.Klass.objects.filter(
                name=klass.name,
                module__project_version__in=other_versions,
            )
            other_versions_of_klass_dict = {
                x.module.project_version: x for x in other_versions_of_klass
            }
            versions = []
            for other_version in other_versions:
                try:
                    other_klass = other_versions_of_klass_dict[other_version]
                except KeyError:
                    url = other_version.get_absolute_url()
                else:
                    url = other_klass.get_absolute_url()

                versions.append(NavData.OtherVersion(name=str(other_version), url=url))
        else:
            versions = [
                NavData.OtherVersion(
                    name=str(other_version), url=other_version.get_absolute_url()
                )
                for other_version in other_versions
            ]

        module_set = projectversion.module_set.prefetch_related("klass_set").order_by(
            "name"
        )
        modules = [
            self._to_module_data(module=m, active_module=module, active_klass=klass)
            for m in module_set
        ]

        nav_data = NavData(
            version_name=str(projectversion),
            other_versions=versions,
            modules=modules,
        )
        return nav_data
