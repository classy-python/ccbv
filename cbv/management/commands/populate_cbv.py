import inspect
import sys

import django
from django.core.management.base import BaseCommand
from django.views import generic

from blessings import Terminal
from cbv.models import Project, ProjectVersion, Module, Klass, Inheritance, KlassAttribute, ModuleAttribute, Method, Function

t = Terminal()


class Command(BaseCommand):
    args = ''
    help = 'Wipes and populates the CBV inspection models.'
    target = generic
    banned_attr_names = (
        '__all__',
        '__builtins__',
        '__class__',
        '__dict__',
        '__doc__',
        '__file__',
        '__module__',
        '__name__',
        '__package__',
        '__path__',
        '__weakref__',
    )

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
        self.attributes = {}
        self.klass_imports = {}
        print t.red('Tree traversal')
        self.process_member(self.target, self.target.__name__)
        self.create_inheritance()
        self.create_attributes()

    def ok_to_add_module(self, member, parent):
        if member.__package__ is None or not member.__name__.startswith(self.target.__name__):
            return False
        return True

    def ok_to_add_klass(self, member, parent):
        if member.__name__.startswith(self.target.__name__):  # TODO: why?
            return False
        try:
            if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
                if parent.__name__ in member.__module__:
                    self.add_new_import_path(member, parent)
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

    def ok_to_add_function(self, member, member_name, parent):
        if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
            return False
        if not inspect.ismodule(parent):
            msg = 'def {}(...): IGNORED because {} is not a module.'.format(
                member.__name__,
                parent.__name__,
            )
            print t.red(msg)
            return False
        return True

    def ok_to_add_attribute(self, member, member_name, parent):
        if inspect.isclass(parent) and member in object.__dict__.values():
                return False

        if member_name in self.banned_attr_names:
            return False
        return True

    ok_to_add_klass_attribute = ok_to_add_module_attribute = ok_to_add_attribute

    def get_code(self, member):
            # Strip unneeded whitespace from beginning of code lines
            lines, start_line = inspect.getsourcelines(member)
            whitespace = len(lines[0]) - len(lines[0].lstrip())
            for i, line in enumerate(lines):
                lines[i] = line[whitespace:]

            # Join code lines into one string
            code = ''.join(lines)

            # Get the method arguments
            i_args, i_varargs, i_keywords, i_defaults = inspect.getargspec(member)
            arguments = inspect.formatargspec(i_args, varargs=i_varargs, varkw=i_keywords, defaults=i_defaults)

            return code, arguments, start_line

    def get_docstring(self, member):
        return inspect.getdoc(member) or ''

    def get_value(self, member):
        return "'{0}'".format(member) if isinstance(member, basestring) else unicode(member)

    def get_filename(self, member):
        # Get full file name
        filename = inspect.getfile(member)

        # Find the system path it's in
        sys_folder = max([p for p in sys.path if p in filename], key=len)

        # Get the part of the file name after the folder on the system path.
        filename = filename[len(sys_folder):]

        # Replace `.pyc` file extensions with `.py`
        if filename[-4:] == '.pyc':
            filename = filename[:-1]
        return filename

    def get_line_number(self, member):
        try:
            return inspect.getsourcelines(member)[1]
        except TypeError:
            return -1

    def add_new_import_path(self, member, parent):
        import_path = parent.__name__
        try:
            current_import_path = self.klass_imports[member]
        except KeyError:
            self.klass_imports[member] = parent.__name__
        else:
            self.update_shortest_import_path(member, current_import_path, import_path)

        try:
            existing_member = Klass.objects.get(
                module__project_version__project__name__iexact='Django',
                module__project_version__version_number=django.get_version(),
                name=member.__name__)
        except Klass.DoesNotExist:
            return

        if self.update_shortest_import_path(member, existing_member.import_path, import_path):
            existing_member.import_path = import_path
            existing_member.save()

    def update_shortest_import_path(self, member, current_import_path, new_import_path):
        new_length = len(new_import_path.split('.'))
        current_length = len(current_import_path.split('.'))
        if new_length < current_length:
            self.klass_imports[member] = new_import_path
            return True
        return False

    def process_member(self, member, member_name, parent=None, parent_node=None):
        # BUILTIN
        if inspect.isbuiltin(member):
            return

        # MODULE
        if inspect.ismodule(member):
            # Only traverse under hierarchy
            if not self.ok_to_add_module(member, parent):
                return

            filename = self.get_filename(member)
            print t.yellow('module ' + member.__name__), filename
            # Create Module object
            this_node = Module.objects.create(
                project_version=self.project_version,
                name=member.__name__,
                docstring=self.get_docstring(member),
                filename=filename
            )
            go_deeper = True

        # CLASS
        elif inspect.isclass(member) and inspect.ismodule(parent):
            if not self.ok_to_add_klass(member, parent):
                return

            self.add_new_import_path(member, parent)
            import_path = self.klass_imports[member]

            start_line = self.get_line_number(member)
            print t.green('class ' + member_name), start_line
            this_node = Klass.objects.create(
                module=parent_node,
                name=member_name,
                docstring=self.get_docstring(member),
                line_number=start_line,
                import_path=import_path
            )
            self.klasses[member] = this_node
            go_deeper = True

        # METHOD
        elif inspect.ismethod(member):
            if not self.ok_to_add_method(member, parent):
                return

            print '    def ' + member_name

            code, arguments, start_line = self.get_code(member)

            # Make the Method
            this_node = Method.objects.create(
                klass=parent_node,
                name=member_name,
                docstring=self.get_docstring(member),
                code=code,
                kwargs=arguments[1:-1],
                line_number=start_line,
            )

            go_deeper = False

        # FUNCTION
        elif inspect.isfunction(member):
            if not self.ok_to_add_function(member, member_name, parent):
                return

            code, arguments, start_line = self.get_code(member)
            print t.blue("def {0}{1}".format(member_name, arguments))

            this_node = Function.objects.create(
                module=parent_node,
                name=member_name,
                docstring=self.get_docstring(member),
                code=code,
                kwargs=arguments[1:-1],
                line_number=start_line,
            )
            go_deeper = False

        # (Class) ATTRIBUTE
        elif inspect.isclass(parent):
            if not self.ok_to_add_klass_attribute(member, member_name, parent):
                return

            value = self.get_value(member)
            attr = (member_name, value)
            start_line = self.get_line_number(member)
            try:
                self.attributes[attr] += [(parent_node, start_line)]
            except KeyError:
                self.attributes[attr] = [(parent_node, start_line)]

            print '    {key} = {val}'.format(key=attr[0], val=attr[1])
            go_deeper = False

        # (Module) ATTRIBUTE
        elif inspect.ismodule(parent):
            if not self.ok_to_add_module_attribute(member, member_name, parent):
                return

            start_line = self.get_line_number(member)
            this_node = ModuleAttribute.objects.create(
                module=parent_node,
                name=member_name,
                value=self.get_value(member),
                line_number=start_line,
            )

            print '{key} = {val}'.format(key=this_node.name, val=this_node.value)
            go_deeper = False

        # INSPECTION. We have to go deeper ;)
        if go_deeper:
            # Go through members
            for submember_name, submember_type in inspect.getmembers(member):
                self.process_member(
                    member=submember_type,
                    member_name=submember_name,
                    parent=member,
                    parent_node=this_node
                )

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
        print ''

    def create_attributes(self):
        print ''
        print t.red('Attributes')

        # Go over each name/value pair to create KlassAttributes
        for name_and_value, klasses in self.attributes.iteritems():

            # Find all the descendants of each Klass.
            descendants = set()
            for klass, start_line in klasses:
                map(descendants.add, klass.get_all_children())

            # By removing descendants from klasses, we leave behind the
            # klass(s) where the value was defined.
            remaining_klasses = [k_and_l for k_and_l in klasses if k_and_l[0] not in descendants]

            # Now we can create the KlassAttributes
            name, value = name_and_value
            for klass, line in remaining_klasses:
                KlassAttribute.objects.create(
                    klass=klass,
                    line_number=line,
                    name=name,
                    value=value
                )

                print '{0}: {1} = {2}'.format(klass, name, value)
