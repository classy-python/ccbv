import inspect


excluded_classes = [
    'BaseException',
    'Exception',
    'classmethod',
    'classonlymethod',
    'dict',
    'object',
]


def get_mro(cls):
    return filter(lambda x: x.__name__ not in excluded_classes, inspect.getmro(cls))
