import inspect
import itertools

import django
from django.core.management.base import BaseCommand, CommandError
from django.views import generic

from cbv.models import Project, ProjectVersion, Module, Klass, Inheritance, Attribute, Method

class Command(BaseCommand):
    args = ''
    help = 'Wipes and populates the CBV inspection models.'
    target = generic
    def handle(self, *args, **options):
        # Delete ALL of the things.
        Project.objects.filter(name='django').delete()

        # Setup Project
        project = Project.objects.create(name='django')
        self.project_version = ProjectVersion.objects.create(
            project=project,
            version_number=django.get_version(),
        )

        self.process_member(self.target)

    def process_member(self, member, parent=None, parent_obj=None):
        print '.'
        # MODULE
        if inspect.ismodule(member):
            if member.__package__ is None or not member.__name__.startswith(self.target.__name__):
                return

            # Create Module object
            module_obj = Module.objects.create(
                project_version=self.project_version,
                name=member.__name__,
                parent=parent_obj
            )

            # Go through members of module
            for member_name, member_type in inspect.getmembers(member):
                self.process_member(member_type, member, module_obj)

        # CLASS
        elif inspect.isclass(member):
            if member.__name__.startswith(self.target.__name__):
                return

            klass = Klass.objects.create(
                module=parent_obj,
                name=member.__name__,
                docstring=inspect.getdoc(member) or ''
            )

            # TODO: Generate class attributes
            for klass_member_name, klass_member_type in inspect.getmembers(member):
                print '-'
                # METHOD
                # TODO
                if inspect.ismethod(klass_member_type):
                    # Strip unneeded whitespace from beginning of line
                    method_lines = inspect.getsourcelines(klass_member_type)[0]
                    whitespace = len(method_lines[0]) - len(method_lines[0].lstrip())
                    for i, line in enumerate(method_lines):
                        method_lines[i] = line[whitespace:]
                    # TODO: Strip out docstring
                    method_code = ''.join(method_lines)
                    i_args, i_varargs, i_keywords, i_defaults = inspect.getargspec(klass_member_type)
                    method_arguments = inspect.formatargspec(i_args, varargs=i_varargs, varkw=i_keywords, defaults=i_defaults)
                    Method.objects.create(
                        klass=klass,
                        name=klass_member_name,
                        docstring=inspect.getdoc(klass_member_type) or '',
                        code=method_code,
                        kwargs=method_arguments[1:-1]
                    )
