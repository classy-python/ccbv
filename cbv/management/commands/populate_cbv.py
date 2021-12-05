import importlib
import inspect
import sys
from collections import defaultdict

import attr
import django
from blessings import Terminal
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.functional import Promise

from cbv import models


t = Terminal()


class LazyAttribute:
    functions = {
        "gettext": "gettext_lazy",
        "reverse": "reverse_lazy",
        "ugettext": "ugettext_lazy",
    }

    def __init__(self, promise):
        func, self.args, self.kwargs, _ = promise.__reduce__()[1]
        try:
            self.lazy_func = self.functions[func.__name__]
        except KeyError:
            msg = f"'{func.__name__}' not in known lazily called functions"
            raise ImproperlyConfigured(msg)

    def __repr__(self):
        arguments = []
        for arg in self.args:
            if isinstance(arg, str):
                arguments.append(f"'{arg}'")
            else:
                arguments.append(arg)
        for key, value in self.kwargs:
            if isinstance(key, str):
                key = f"'{key}'"
            if isinstance(value, str):
                value = f"'{value}'"
            arguments.append(f"{key}: {value}")
        func = self.lazy_func
        arguments = ", ".join(arguments)
        return f"{func}({arguments})"


BANNED_ATTR_NAMES = (
    "__all__",
    "__builtins__",
    "__class__",
    "__dict__",
    "__doc__",
    "__file__",
    "__module__",
    "__name__",
    "__package__",
    "__path__",
    "__spec__",
    "__weakref__",
)


class Command(BaseCommand):
    args = ""
    help = "Wipes and populates the CBV inspection models."

    def handle(self, *args, **options):
        CBVImporter().start()


@attr.frozen
class Module:
    name: str
    docstring: str
    filename: str


@attr.frozen
class Klass:
    name: str
    module: str
    docstring: str
    line_number: int
    path: str
    bases: list[str]
    model: models.Klass


@attr.frozen
class KlassAttribute:
    name: str
    value: str
    line_number: int
    parent_node: models.Klass


@attr.frozen
class Method:
    name: str
    code: str
    docstring: str
    kwargs: list[str]
    line_number: int
    parent_node: models.Klass


# TODO (Charlie): If this object continues to exist, it'll want a better name.
class CBVImporter:
    def start(self):
        django_version = django.get_version()
        # We don't really care about deleting the ProjectVersion here in particular.
        # (Note that we re-create it below.)
        # Instead, we're using the cascading delete to remove all the dependent objects.
        models.ProjectVersion.objects.filter(
            project__name__iexact="Django",
            version_number=django_version,
        ).delete()
        models.Inheritance.objects.filter(
            parent__module__project_version__project__name__iexact="Django",
            parent__module__project_version__version_number=django_version,
        ).delete()

        # Setup Project
        self.project_version = models.ProjectVersion.objects.create(
            project=models.Project.objects.get_or_create(name="Django")[0],
            version_number=django_version,
        )

        klasses = []
        attributes = defaultdict(list)
        self.klass_imports = {}
        self.module_models: dict[str, models.Module] = {}

        # Set sources appropriate to this version
        module_paths = settings.CBV_SOURCES.keys()
        print(t.red("Tree traversal"))
        members = self.process_modules(module_paths=module_paths)
        for member in members:
            if isinstance(member, models.Module):
                self.module_models[member.name] = member
                print(t.yellow("module " + member.name), member.filename)
            elif isinstance(member, models.Klass):
                print(t.green("class " + member.name), member.line_number)
            elif isinstance(member, KlassAttribute):
                print(f"    {member.name} = {member.value}")
                attributes[(member.name, member.value)] += [
                    (member.parent_node, member.line_number)
                ]
            elif isinstance(member, Method):
                print("    def " + member.name)
                models.Method.objects.create(
                    klass=member.parent_node,
                    name=member.name,
                    docstring=member.docstring,
                    code=member.code,
                    kwargs=member.kwargs,
                    line_number=member.line_number,
                )
            elif isinstance(member, Klass):
                klasses.append(member)

        create_inheritance(klasses)
        create_attributes(attributes)

    def add_new_import_path(self, member, parent):
        import_path = parent.__name__
        try:
            current_import_path = self.klass_imports[member]
        except KeyError:
            self.klass_imports[member] = parent.__name__
        else:
            self.update_shortest_import_path(member, current_import_path, import_path)

        try:
            existing_member = models.Klass.objects.get(
                module__project_version__project__name__iexact="Django",
                module__project_version__version_number=django.get_version(),
                name=member.__name__,
            )
        except models.Klass.DoesNotExist:
            return

        if self.update_shortest_import_path(
            member, existing_member.import_path, import_path
        ):
            existing_member.import_path = import_path
            existing_member.save()

    def update_shortest_import_path(self, member, current_import_path, new_import_path):
        new_length = len(new_import_path.split("."))
        current_length = len(current_import_path.split("."))
        if new_length < current_length:
            self.klass_imports[member] = new_import_path
            return True
        return False

    def process_modules(self, *, module_paths):
        modules = []
        for module_path in module_paths:
            try:
                modules.append(importlib.import_module(module_path))
            except ImportError:
                pass

        for module in modules:
            module_name = module.__name__

            yield from self._process_member(
                member=module,
                member_name=module_name,
                root_module_name=module_name,
                parent=None,
                parent_node=None,
            )

    def _process_member(
        self, *, member, member_name, root_module_name, parent, parent_node
    ):
        def handle_module(module, root_module_name):
            module_name = module.__name__
            # Only traverse under hierarchy
            if not module_name.startswith(root_module_name):
                return None

            filename = get_filename(module)
            # Create Module object
            module_data = Module(
                name=module_name,
                docstring=get_docstring(module),
                filename=filename,
            )
            this_node = models.Module.objects.create(
                project_version=self.project_version,
                name=module_data.name,
                docstring=module_data.docstring,
                filename=module_data.filename,
            )
            yield this_node
            # Go through members
            yield from self._process_submembers(
                root_module_name=root_module_name,
                parent=module,
                parent_node=this_node,
            )

        def handle_class_on_module(member, member_name, parent):
            if not member.__module__.startswith(parent.__name__):
                return None

            self.add_new_import_path(member, parent)

            if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
                return None

            import_path = self.klass_imports[member]

            start_line = get_line_number(member)
            docstring = get_docstring(member)
            this_node = models.Klass.objects.create(
                module=self.module_models[parent.__name__],
                name=member_name,
                docstring=docstring,
                line_number=start_line,
                import_path=import_path,
            )
            klass = Klass(
                name=member.__name__,
                module=member.__module__,
                docstring=docstring,
                line_number=start_line,
                path=_full_path(member),
                bases=[_full_path(k) for k in member.__bases__],
                model=this_node,
            )
            yield klass
            yield this_node
            # Go through members
            yield from self._process_submembers(
                root_module_name=root_module_name,
                parent=member,
                parent_node=this_node,
            )

        def handle_function_or_method(member, member_name, parent, parent_node):
            # Decoration
            while getattr(member, "__wrapped__", None):
                member = member.__wrapped__

            # Checks
            if not ok_to_add_method(member, parent):
                return

            code, arguments, start_line = get_code(member)

            yield Method(
                name=member_name,
                docstring=get_docstring(member),
                code=code,
                kwargs=arguments[1:-1],
                line_number=start_line,
                parent_node=parent_node,
            )

        def handle_class_attribute(member, member_name, parent, parent_node):
            # Replace lazy function call with an object representing it
            if isinstance(member, Promise):
                member = LazyAttribute(member)

            if not ok_to_add_attribute(member, member_name, parent):
                return

            yield KlassAttribute(
                name=member_name,
                value=get_value(member),
                line_number=get_line_number(member),
                parent_node=parent_node,
            )

        # BUILTIN
        if inspect.isbuiltin(member):
            pass

        # MODULE
        elif inspect.ismodule(member):
            yield from handle_module(member, root_module_name)

        # CLASS
        elif inspect.isclass(member) and inspect.ismodule(parent):
            yield from handle_class_on_module(member, member_name, parent)

        # METHOD
        elif inspect.ismethod(member) or inspect.isfunction(member):
            yield from handle_function_or_method(
                member, member_name, parent, parent_node
            )

        # (Class) ATTRIBUTE
        elif inspect.isclass(parent):
            yield from handle_class_attribute(member, member_name, parent, parent_node)

    def _process_submembers(self, *, parent, root_module_name, parent_node):
        for submember_name, submember_type in inspect.getmembers(parent):
            yield from self._process_member(
                member=submember_type,
                member_name=submember_name,
                root_module_name=root_module_name,
                parent=parent,
                parent_node=parent_node,
            )


def _full_path(klass: type) -> str:
    return f"{klass.__module__}.{klass.__name__}"


def create_attributes(attributes):
    print("")
    print(t.red("Attributes"))

    # Go over each name/value pair to create KlassAttributes
    for name_and_value, klasses in attributes.items():

        # Find all the descendants of each Klass.
        descendants = set()
        for klass, start_line in klasses:
            for child in klass.get_all_children():
                descendants.add(child)

        # By removing descendants from klasses, we leave behind the
        # klass(s) where the value was defined.
        remaining_klasses = [
            k_and_l for k_and_l in klasses if k_and_l[0] not in descendants
        ]

        # Now we can create the KlassAttributes
        name, value = name_and_value
        for klass, line in remaining_klasses:
            models.KlassAttribute.objects.create(
                klass=klass, line_number=line, name=name, value=value
            )

            print(f"{klass}: {name} = {value}")


def create_inheritance(klasses):
    klass_lookup = {k.path: k for k in klasses}
    print("")
    print(t.red("Inheritance"))
    for klass_data in klasses:
        print("")
        print(t.green(klass_data.name), end=" ")
        direct_ancestors = klass_data.bases
        for i, ancestor in enumerate(direct_ancestors):
            if ancestor in klass_lookup:
                print(".", end=" ")
                models.Inheritance.objects.create(
                    parent=klass_lookup[ancestor].model, child=klass_data.model, order=i
                )
    print("")


def get_code(member):
    # Strip unneeded whitespace from beginning of code lines
    lines, start_line = inspect.getsourcelines(member)
    whitespace = len(lines[0]) - len(lines[0].lstrip())
    for i, line in enumerate(lines):
        lines[i] = line[whitespace:]

    # Join code lines into one string
    code = "".join(lines)

    # Get the method arguments
    arguments = inspect.formatargspec(*inspect.getfullargspec(member))

    return code, arguments, start_line


def get_docstring(member):
    return inspect.getdoc(member) or ""


def get_filename(member):
    # Get full file name
    filename = inspect.getfile(member)

    # Find the system path it's in
    sys_folder = max((p for p in sys.path if p in filename), key=len)

    # Get the part of the file name after the folder on the system path.
    filename = filename[len(sys_folder) :]

    # Replace `.pyc` file extensions with `.py`
    if filename[-4:] == ".pyc":
        filename = filename[:-1]
    return filename


def get_line_number(member):
    try:
        return inspect.getsourcelines(member)[1]
    except TypeError:
        return -1


def get_value(member):
    return f"'{member}'" if isinstance(member, str) else str(member)


def ok_to_add_attribute(member, member_name, parent):
    if inspect.isclass(parent) and member in object.__dict__.values():
        return False

    if member_name in BANNED_ATTR_NAMES:
        return False
    return True


def ok_to_add_method(member, parent):
    if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
        return False

    if not inspect.isclass(parent):
        msg = "def {}(...): IGNORED because {} is not a class.".format(
            member.__name__,
            parent.__name__,
        )
        print(t.red(msg))
        return False

    # Use line inspection to work out whether the method is defined on this
    # klass. Possibly not the best way, but I can't think of another atm.
    lines, start_line = inspect.getsourcelines(member)
    parent_lines, parent_start_line = inspect.getsourcelines(parent)
    if start_line < parent_start_line or start_line > parent_start_line + len(
        parent_lines
    ):
        return False
    return True
