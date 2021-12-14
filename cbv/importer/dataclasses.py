import attr


@attr.frozen
class Klass:
    name: str
    module: str
    docstring: str
    line_number: int
    path: str
    bases: list[str]


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


# TODO (Charlie): This wants a better name.
@attr.frozen
class PotentialImport:
    klass_name: str
    klass_path: str
    import_path: str
