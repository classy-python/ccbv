import __builtin__
import collections
import inspect
import pydoc


def classify(klass, obj, name=None, mod=None, *ignored):
    if not inspect.isclass(obj):
        raise Exception

    mro = list(reversed(filter(lambda x: x is not __builtin__.object, inspect.getmro(obj))))

    klass.update({
        'name': obj.__name__,
        'docstring': pydoc.getdoc(obj),
        'ancestors': [k.__name__ for k in mro[:-1]],
        'parents': inspect.getclasstree([obj])[-1][0][1]
    })

    for cls in mro:
        members = filter(lambda m: m[0] == '__init__' or not m[0].startswith('__'), inspect.getmembers(cls))
        methods = filter(lambda m: inspect.ismethod(m[1]), members)
        attributes = filter(lambda m: not inspect.ismethod(m[1]), members)

        # ATTRIBUTES
        for name, obj in attributes:
            attr = klass['attributes'][name]

            # If we already know about this attr/value then ignore
            if obj not in [a['object'] for a in attr]:
                attr.append({'object': obj, 'defining_class': cls})

        # METHODS
        for name, func in methods:
            method = klass['methods'][name]

            # Get source line details
            lines, start_line = inspect.getsourcelines(func)
            code = ''.join(lines).strip()

            if code in [m['code'] for m in method]:
                continue

            # Get the method arguments
            args, varargs, keywords, defaults = inspect.getargspec(func)
            arguments = inspect.formatargspec(args, varargs=varargs, varkw=keywords, defaults=defaults)

            data = {
                'docstring': pydoc.getdoc(func),
                'defining_class': cls,
                'arguments': arguments,
                'code': code,
                'lines': {'start': start_line, 'total': len(lines)},
                'file': inspect.getsourcefile(func)
            }
            method.append(data)

    # sort attributes & methods
    klass['attributes'] = collections.OrderedDict(sorted(klass['attributes'].items()))
    klass['methods'] = collections.OrderedDict(sorted(klass['methods'].items(), key=lambda m: m[0].strip('__')))

    return klass


def build(thing):
    """Build a dictionary mapping of a class."""
    klass = {
        'attributes': collections.defaultdict(list),
        'methods': collections.defaultdict(list),
        'properties': [],
        'ancestors': [],
        'parents': [],
    }

    obj, name = pydoc.resolve(thing, forceload=0)
    if type(obj) is pydoc._OLD_INSTANCE_TYPE:
        # If the passed obj is an instance of an old-style class,
        # dispatch its available methods instead of its value.
        obj = obj.__class__
    return classify(klass, obj, name)
