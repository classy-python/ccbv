from collections import defaultdict
from collections.abc import Mapping, Sequence

from cbv import models
from cbv.importer.dataclasses import Klass, KlassAttribute, Method, Module
from cbv.importer.importers import CodeImporter


class DBStorage:
    def import_project_version(
        self, *, importer: CodeImporter, project_name: str, project_version: str
    ) -> None:
        self._wipe_clashing_data(
            project_name=project_name, project_version=project_version
        )

        # Setup Project
        project_version_pk = models.ProjectVersion.objects.create(
            project=models.Project.objects.get_or_create(name=project_name)[0],
            version_number=project_version,
        ).pk

        klasses = []
        attributes: defaultdict[tuple[str, str], list[tuple[str, int]]] = defaultdict(
            list
        )
        klass_models: dict[str, models.Klass] = {}
        module_models: dict[str, models.Module] = {}
        method_models: list[models.Method] = []

        for member in importer.generate_code_data():
            if isinstance(member, Module):
                module_model = models.Module.objects.create(
                    project_version_id=project_version_pk,
                    name=member.name,
                    docstring=member.docstring,
                    filename=member.filename,
                )
                module_models[member.name] = module_model
            elif isinstance(member, KlassAttribute):
                attributes[(member.name, member.value)] += [
                    (member.klass_path, member.line_number)
                ]
            elif isinstance(member, Method):
                method = models.Method(
                    klass=klass_models[member.klass_path],
                    name=member.name,
                    docstring=member.docstring,
                    code=member.code,
                    kwargs=member.kwargs,
                    line_number=member.line_number,
                )
                method_models.append(method)
            elif isinstance(member, Klass):
                klass_model = models.Klass.objects.create(
                    module=module_models[member.module],
                    name=member.name,
                    docstring=member.docstring,
                    line_number=member.line_number,
                    import_path=member.best_import_path,
                )
                klass_models[member.path] = klass_model
                klasses.append(member)

        models.Method.objects.bulk_create(method_models)
        create_inheritance(klasses, klass_models)
        create_attributes(attributes, klass_models)
        print("Stored:")
        print(f" Modules: {len(module_models)}")
        print(f" Classes: {len(klasses)}")
        print(f" Methods: {len(method_models)}")
        print(f" Attributes: {models.KlassAttribute.objects.count()}")

    def _wipe_clashing_data(self, *, project_name: str, project_version: str) -> None:
        """Delete existing data in the DB to make way for this new import."""
        # We don't really care about deleting the ProjectVersion here in particular.
        # In fact, we'll re-create it later.
        # Instead, we're using the cascading delete to remove all the dependent objects.
        models.ProjectVersion.objects.filter(
            version_number=project_version,
        ).delete()
        models.Inheritance.objects.filter(
            parent__module__project_version__version_number=project_version,
        ).delete()


def create_attributes(
    attributes: Mapping[tuple[str, str], Sequence[tuple[str, int]]],
    klass_lookup: Mapping[str, models.Klass],
) -> None:
    # Go over each name/value pair to create KlassAttributes
    attribute_models = []
    for (name, value), klasses in attributes.items():

        # Find all the descendants of each Klass.
        descendants = set()
        for klass_path, start_line in klasses:
            klass = klass_lookup[klass_path]
            for child in klass.get_all_children():
                descendants.add(child)

        # By removing descendants from klasses, we leave behind the
        # klass(s) where the value was defined.
        remaining_klasses = [
            k_and_l
            for k_and_l in klasses
            if klass_lookup[k_and_l[0]] not in descendants
        ]

        # Now we can create the KlassAttributes
        for klass_path, line in remaining_klasses:
            klass = klass_lookup[klass_path]
            attribute_models.append(
                models.KlassAttribute(
                    klass=klass, line_number=line, name=name, value=value
                )
            )

    models.KlassAttribute.objects.bulk_create(attribute_models)


def create_inheritance(
    klasses: Sequence[Klass], klass_lookup: Mapping[str, models.Klass]
) -> None:
    inheritance_models = []
    for klass_data in klasses:
        direct_ancestors = klass_data.bases
        for i, ancestor in enumerate(direct_ancestors):
            if ancestor not in klass_lookup:
                continue
            inheritance_models.append(
                models.Inheritance(
                    parent=klass_lookup[ancestor],
                    child=klass_lookup[klass_data.path],
                    order=i,
                )
            )
    models.Inheritance.objects.bulk_create(inheritance_models)
