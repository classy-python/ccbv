import factory

from .models import Inheritance, Klass, Module, Project, ProjectVersion


class ProjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = Project
    name = factory.Sequence(lambda n: 'project{0}'.format(n))


class ProjectVersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProjectVersion
    project = factory.SubFactory(ProjectFactory)
    version_number = factory.Sequence(lambda n: str(n))


class ModuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Module
    project_version = factory.SubFactory(ProjectVersionFactory)
    name = factory.Sequence(lambda n: 'module{0}'.format(n))


class KlassFactory(factory.DjangoModelFactory):
    class Meta:
        model = Klass
    module = factory.SubFactory(ModuleFactory)
    name = factory.Sequence(lambda n: 'klass{0}'.format(n))
    line_number = 1
    import_path = factory.LazyAttribute(
        lambda a: '{project}.{module}'.format(
            project=a.module.project_version.project.name,
            module=a.module.name,
        )
    )


class InheritanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Inheritance
    parent = factory.SubFactory(KlassFactory)
    child = factory.SubFactory(KlassFactory)
    order = 1
