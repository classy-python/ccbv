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
        ProjectVersion.objects.filter(
            project__name__iexact='django',
            version_number=django.get_version(),
        ).delete()
        Inheritance.objects.filter(
            parent__module__project_version__project__name__iexact='django',
            parent__module__project_version__version_number=django.get_version(),
        ).delete()

        # Setup Project
        self.project_version = ProjectVersion.objects.create(
            project=Project.objects.get_or_create(name='django')[0],
            version_number=django.get_version(),
        )

        self.klasses = {}
        self.process_member(self.target)
        self.create_inheritance()

    def process_member(self, member, parent=None, parent_obj=None):
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

            klass_source_file = inspect.getsourcefile(member)
            parent_source_file = inspect.getsourcefile(parent)
            if not klass_source_file == parent_source_file:
                return

            print member.__name__
            klass_source = inspect.getsourcelines(member)
            klass_line_start = klass_source[1]
            klass_line_end = klass_line_start + len(klass_source[0])

            klass = Klass.objects.create(
                module=parent_obj,
                name=member.__name__,
                docstring=inspect.getdoc(member) or ''
            )

            self.klasses[member] = klass

            # TODO: Generate class attributes
            for klass_member_name, klass_member_type in inspect.getmembers(member):
                # METHOD
                if inspect.ismethod(klass_member_type):
                    # Use line inspection to work out whether the method is defined on this klass
                    method_source_file = inspect.getsourcefile(klass_member_type)
                    if not method_source_file == klass_source_file:
                        continue
                    method_source = inspect.getsourcelines(klass_member_type)
                    method_lines, method_line_start = method_source
                    if method_line_start < klass_line_start or method_line_start > klass_line_end:
                        continue

                    # Strip unneeded whitespace from beginning of line
                    whitespace = len(method_lines[0]) - len(method_lines[0].lstrip())
                    for i, line in enumerate(method_lines):
                        method_lines[i] = line[whitespace:]
                    # TODO: Strip out docstring
                    method_code = ''.join(method_lines)
                    i_args, i_varargs, i_keywords, i_defaults = inspect.getargspec(klass_member_type)
                    method_arguments = inspect.formatargspec(i_args, varargs=i_varargs, varkw=i_keywords, defaults=i_defaults)
                    # Make the method
                    Method.objects.create(
                        klass=klass,
                        name=klass_member_name,
                        docstring=inspect.getdoc(klass_member_type) or '',
                        code=method_code,
                        kwargs=method_arguments[1:-1]
                    )

    def create_inheritance(self):
        for klass, representation in self.klasses.iteritems():
            direct_ancestors = inspect.getclasstree([klass])[-1][0][1]
            for i, ancestor in enumerate(direct_ancestors):
                if ancestor in self.klasses:
                    Inheritance.objects.create(
                        parent=self.klasses[ancestor],
                        child=representation,
                        order=i
                    )
