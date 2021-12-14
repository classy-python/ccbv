"""Data classes used in the process of importing code."""
import attr


@attr.frozen
class Klass:
    name: str
    module: str
    docstring: str
    line_number: int
    path: str
    bases: list[str]
    best_import_path: str


@attr.frozen
class KlassAttribute:
    name: str
    value: str
    line_number: int
    klass_path: str


@attr.frozen
class Method:
    name: str
    code: str
    docstring: str
    kwargs: list[str]
    line_number: int
    klass_path: str


@attr.frozen
class Module:
    name: str
    docstring: str
    filename: str
