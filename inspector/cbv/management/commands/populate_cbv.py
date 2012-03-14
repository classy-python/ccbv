import inspect

import django
from django.core.management.base import BaseCommand
from django.views import generic

from blessings import Terminal
from cbv.models import Project, ProjectVersion, Module, Klass, Inheritance, Attribute, Method

t = Terminal()


class Command(BaseCommand):
    args = ''
    help = 'Wipes and populates the CBV inspection models.'
    target = generic

    def handle(self, *args, **options):
        # Delete ALL of the things.
        ProjectVersion.objects.filter(
            project__name__iexact='Django',
            version_number=django.get_version(),
        ).delete()
        Inheritance.objects.filter(
            parent__module__project_version__project__name__iexact='Django',
            parent__module__project_version__version_number=django.get_version(),
        ).delete()

        # Setup Project
        self.project_version = ProjectVersion.objects.create(
            project=Project.objects.get_or_create(name='Django')[0],
            version_number=django.get_version(),
        )

        self.klasses = {}
        print t.red('Tree traversal')
        self.process_member(self.target)
        self.create_inheritance()

    def ok_to_add_module(self, member, parent):
        if member.__package__ is None or not member.__name__.startswith(self.target.__name__):
            return False
        return True

    def ok_to_add_klass(self, member, parent):
        if member.__name__.startswith(self.target.__name__):  # TODO: why?
            return False
        try:
            if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
                return False
        except TypeError:
            return False
        return True

    def ok_to_add_method(self, member, parent):
        if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
            return False

        # Use line inspection to work out whether the method is defined on this
        # klass. Possibly not the best way, but I can't think of another atm.
        lines, start_line = inspect.getsourcelines(member)
        parent_lines, parent_start_line = inspect.getsourcelines(parent)
        if start_line < parent_start_line or start_line > parent_start_line + len(parent_lines):
            return False
        return True

    def process_member(self, member, parent=None, parent_node=None):
        # BUILTIN
        if inspect.isbuiltin(member):
            return

        go_deeper = True

        # MODULE
        if inspect.ismodule(member):
            # Only traverse under hierarchy
            if not self.ok_to_add_module(member, parent):
                return

            print t.yellow('module ' + member.__name__)
            # Create Module object
            this_node = Module.objects.create(
                project_version=self.project_version,
                name=member.__name__,
                parent=parent_node,
                docstring=inspect.getdoc(member) or '',
            )

        # CLASS
        elif inspect.isclass(member):
            if not self.ok_to_add_klass(member, parent):
                return

            print t.green('class ' + member.__name__)
            this_node = Klass.objects.create(
                module=parent_node,
                name=member.__name__,
                docstring=inspect.getdoc(member) or '',
            )
            self.klasses[member] = this_node

        # METHOD
        elif inspect.ismethod(member):
            if not self.ok_to_add_method(member, parent):
                return

            print '    def ' + member.__name__
            # Strip unneeded whitespace from beginning of code lines
            lines, start_line = inspect.getsourcelines(member)
            whitespace = len(lines[0]) - len(lines[0].lstrip())
            for i, line in enumerate(lines):
                lines[i] = line[whitespace:]

            # TODO?: Strip out docstring.

            # Join code lines into one string
            code = ''.join(lines)

            # Get the method arguments
            i_args, i_varargs, i_keywords, i_defaults = inspect.getargspec(member)
            arguments = inspect.formatargspec(i_args, varargs=i_varargs, varkw=i_keywords, defaults=i_defaults)

            # Make the Method
            this_node = Method.objects.create(
                klass=parent_node,
                name=member.__name__,
                docstring=inspect.getdoc(member) or '',
                code=code,
                kwargs=arguments[1:-1],
            )

            go_deeper = False

        # TODO:
        # FUNCTION
        # CODE SNIPPET:
        #     especially ATTRIBUTEs on CLASSES

        else:
            return

        if go_deeper:
            # Go through members
            for member_name, member_type in inspect.getmembers(member):
                self.process_member(member_type, member, this_node)

    def create_inheritance(self):
        print ''
        print t.red('Inheritance')
        for klass, representation in self.klasses.iteritems():
            print ''
            print t.green(representation.__unicode__()),
            direct_ancestors = inspect.getclasstree([klass])[-1][0][1]
            for i, ancestor in enumerate(direct_ancestors):
                if ancestor in self.klasses:
                    print '.',
                    Inheritance.objects.create(
                        parent=self.klasses[ancestor],
                        child=representation,
                        order=i
                    )
