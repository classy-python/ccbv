import importlib
import inspect
import sys
from collections.abc import Iterator
from typing import Protocol

import attr
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise

from cbv.importer.dataclasses import CodeElement, Klass, KlassAttribute, Method, Module


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


class CodeImporter(Protocol):  # nocoverage: protocol
    def generate_code_data(self) -> Iterator[CodeElement]: ...


@attr.frozen
class InspectCodeImporter:
    """Generates code structure classes by using the inspect module."""

    module_paths: list[str]

    def generate_code_data(self) -> Iterator[CodeElement]:
        modules = []
        for module_path in self.module_paths:
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
            )

    def _process_member(
        self, *, member, member_name, root_module_name, parent
    ) -> Iterator[CodeElement]:
        # BUILTIN
        if inspect.isbuiltin(member):
            pass

        # MODULE
        elif inspect.ismodule(member):
            yield from self._handle_module(member, root_module_name)

        # CLASS
        elif inspect.isclass(member) and inspect.ismodule(parent):
            yield from self._handle_class_on_module(member, parent, root_module_name)

        # METHOD
        elif inspect.ismethod(member) or inspect.isfunction(member):
            yield from self._handle_function_or_method(member, member_name, parent)

        # (Class) ATTRIBUTE
        elif inspect.isclass(parent):
            yield from self._handle_class_attribute(member, member_name, parent)

    def _process_submembers(self, *, parent, root_module_name) -> Iterator[CodeElement]:
        for submember_name, submember_type in inspect.getmembers(parent):
            yield from self._process_member(
                member=submember_type,
                member_name=submember_name,
                root_module_name=root_module_name,
                parent=parent,
            )

    def _handle_module(self, module, root_module_name) -> Iterator[CodeElement]:
        module_name = module.__name__
        # Only traverse under hierarchy
        if not module_name.startswith(root_module_name):
            return None

        filename = get_filename(module)
        # Create Module object
        yield Module(
            name=module_name,
            docstring=get_docstring(module),
            filename=filename,
        )
        # Go through members
        yield from self._process_submembers(
            root_module_name=root_module_name, parent=module
        )

    def _handle_class_on_module(
        self, member, parent, root_module_name
    ) -> Iterator[CodeElement]:
        if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
            return None

        if issubclass(member, Exception | Warning):
            return None

        yield Klass(
            name=member.__name__,
            module=member.__module__,
            docstring=get_docstring(member),
            line_number=get_line_number(member),
            path=_full_path(member),
            bases=[_full_path(k) for k in member.__bases__],
            best_import_path=_get_best_import_path_for_class(member),
        )
        # Go through members
        yield from self._process_submembers(
            root_module_name=root_module_name, parent=member
        )

    def _handle_function_or_method(
        self, member, member_name, parent
    ) -> Iterator[Method]:
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
            klass_path=_full_path(parent),
        )

    def _handle_class_attribute(
        self, member, member_name, parent
    ) -> Iterator[KlassAttribute]:
        # Replace lazy function call with an object representing it
        if isinstance(member, Promise):
            member = LazyAttribute(member)

        if not ok_to_add_attribute(member, member_name, parent):
            return

        yield KlassAttribute(
            name=member_name,
            value=get_value(member),
            line_number=get_line_number(member),
            klass_path=_full_path(parent),
        )


def _get_best_import_path_for_class(klass: type) -> str:
    module_path = best_path = klass.__module__

    while module_path := module_path.rpartition(".")[0]:
        module = importlib.import_module(module_path)
        if getattr(module, klass.__name__, None) == klass:
            best_path = module_path
    return best_path


def _full_path(klass: type) -> str:
    return f"{klass.__module__}.{klass.__name__}"


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


def get_docstring(member) -> str:
    return inspect.getdoc(member) or ""


def get_filename(member) -> str:
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


def get_line_number(member) -> int:
    try:
        return inspect.getsourcelines(member)[1]
    except TypeError:
        return -1


def get_value(member) -> str:
    return f"'{member}'" if isinstance(member, str) else str(member)


def ok_to_add_attribute(member, member_name, parent) -> bool:
    if inspect.isclass(parent) and member in object.__dict__.values():
        return False

    if member_name in BANNED_ATTR_NAMES:
        return False
    return True


def ok_to_add_method(member, parent) -> bool:
    if inspect.getsourcefile(member) != inspect.getsourcefile(parent):
        return False

    if not inspect.isclass(parent):
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


class LazyAttribute:
    functions = {
        "gettext": "gettext_lazy",
        "reverse": "reverse_lazy",
        "ugettext": "ugettext_lazy",
    }

    def __init__(self, promise: Promise) -> None:
        func, self.args, self.kwargs, _ = promise.__reduce__()[1]
        try:
            self.lazy_func = self.functions[func.__name__]
        except KeyError:
            msg = f"'{func.__name__}' not in known lazily called functions"
            raise ImproperlyConfigured(msg)

    def __repr__(self) -> str:
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
        argument_string = ", ".join(arguments)
        return f"{func}({argument_string})"
