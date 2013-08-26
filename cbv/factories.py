import factory

from .models import Inheritance, Klass, Module, Project, ProjectVersion


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project
    name = factory.Sequence(lambda n: 'project{0}'.format(n))


class ProjectVersionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ProjectVersion
    project = factory.SubFactory(ProjectFactory)
    version_number = factory.Sequence(lambda n: str(n))


class ModuleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Module
    project_version = factory.SubFactory(ProjectVersionFactory)
    name = factory.Sequence(lambda n: 'module{0}'.format(n))


class KlassFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Klass
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
    FACTORY_FOR = Inheritance
    parent = factory.SubFactory(KlassFactory)
    child = factory.SubFactory(KlassFactory)
    order = 1
