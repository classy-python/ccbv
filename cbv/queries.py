import attrs

from cbv import models
from cbv.models import DjangoURLService


@attrs.frozen
class VersionSwitcher:
    version_name: str
    other_versions: list["OtherVersion"]
    project_name: str = "Django"

    @attrs.frozen
    class OtherVersion:
        name: str
        url: str


@attrs.frozen
class NavData:
    modules: list["Module"]

    @attrs.frozen
    class Module:
        source_name: str
        short_name: str
        classes: list["NavData.Klass"]
        active: bool

    @attrs.frozen
    class Klass:
        name: str
        url: str
        active: bool


class NavBuilder:
    def _to_module_data(
        self,
        module: models.Module,
        active_module: models.Module | None,
        active_klass: models.Klass | None,
    ) -> "NavData.Module":
        url_service = DjangoURLService()
        return NavData.Module(
            source_name=module.source_name(),
            short_name=module.short_name(),
            classes=[
                NavData.Klass(
                    name=klass.name,
                    url=url_service.class_detail(
                        class_name=klass.name,
                        module_name=klass.module.name,
                        version_number=klass.module.project_version.version_number,
                    ),
                    active=klass == active_klass,
                )
                for klass in module.klass_set.all()
            ],
            active=module == active_module,
        )

    def make_version_switcher(
        self,
        project_version: models.ProjectVersion,
        klass: models.Klass | None = None,
    ) -> VersionSwitcher:
        other_versions = models.ProjectVersion.objects.exclude(pk=project_version.pk)
        url_service = DjangoURLService()
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
                    url = url_service.class_detail(
                        class_name=other_klass.name,
                        module_name=other_klass.module.name,
                        version_number=other_version.version_number,
                    )

                versions.append(
                    VersionSwitcher.OtherVersion(
                        name=other_version.version_number, url=url
                    )
                )
        else:
            versions = [
                VersionSwitcher.OtherVersion(
                    name=other_version.version_number,
                    url=other_version.get_absolute_url(),
                )
                for other_version in other_versions
            ]

        version_switcher = VersionSwitcher(
            version_name=project_version.version_number,
            other_versions=versions,
        )
        return version_switcher

    def get_nav_data(
        self,
        project_version: models.ProjectVersion,
        module: models.Module | None = None,
        klass: models.Klass | None = None,
    ) -> NavData:
        module_set = project_version.module_set.prefetch_related("klass_set").order_by(
            "name"
        )
        modules = [
            self._to_module_data(module=m, active_module=module, active_klass=klass)
            for m in module_set
        ]
        nav_data = NavData(modules=modules)
        return nav_data
