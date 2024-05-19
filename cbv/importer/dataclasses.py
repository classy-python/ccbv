"""Data classes used in the process of importing code."""

import abc

import attr


class CodeElement(abc.ABC):
    """A base for classes used to represent code."""


@attr.frozen
class Klass(CodeElement):
    name: str
    module: str
    docstring: str
    line_number: int
    path: str
    bases: list[str]
    best_import_path: str


@attr.frozen
class KlassAttribute(CodeElement):
    name: str
    value: str
    line_number: int
    klass_path: str


@attr.frozen
class Method(CodeElement):
    name: str
    code: str
    docstring: str
    kwargs: list[str]
    line_number: int
    klass_path: str


@attr.frozen
class Module(CodeElement):
    name: str
    docstring: str
    filename: str
