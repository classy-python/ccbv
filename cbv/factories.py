import factory

from .models import Inheritance, Klass, Module, Project, ProjectVersion


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence("project{}".format)


class ProjectVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectVersion

    project = factory.SubFactory(ProjectFactory)
    version_number = factory.Sequence(lambda n: str(n))


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    project_version = factory.SubFactory(ProjectVersionFactory)
    name = factory.Sequence("module{}".format)


class KlassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Klass

    module = factory.SubFactory(ModuleFactory)
    name = factory.Sequence("klass{}".format)
    line_number = 1
    import_path = factory.LazyAttribute(
        lambda a: "{project}.{module}".format(
            project=a.module.project_version.project.name,
            module=a.module.name,
        )
    )


class InheritanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inheritance

    parent = factory.SubFactory(KlassFactory)
    child = factory.SubFactory(KlassFactory)
    order = 1
