import collections
import inspect
import pydoc

from .utils import get_mro


def build(thing):
    """Build a dictionary mapping of a class."""
    klass, name = pydoc.resolve(thing, forceload=0)
    mro = list(reversed(get_mro(klass)))

    data = {
        'ancestors': collections.OrderedDict([(k.__name__, k.__module__) for k in mro[:-1]]),
        'attributes': collections.defaultdict(list),
        'docstring': pydoc.getdoc(klass),
        'methods': collections.defaultdict(list),
        'module': klass.__module__,
        'name': name,
        'parents': inspect.getclasstree([klass])[-1][0][1],
        'source_url': source_url,
    }

    if not inspect.isclass(klass):
        raise Exception

    for cls in mro:
        members = filter(lambda m: m[0] == '__init__' or not m[0].startswith('__'), inspect.getmembers(cls))
        methods = filter(lambda m: inspect.ismethod(m[1]), members)
        attributes = filter(lambda m: not inspect.ismethod(m[1]), members)

        # ATTRIBUTES
        for name, obj in attributes:
            attr = data['attributes'][name]

            # If we already know about this attr/value then ignore
            if obj not in [a['object'] for a in attr]:
                attr.append({'object': obj, 'defining_class': cls})

        # METHODS
        for name, func in methods:
            method = data['methods'][name]

            # Get source line details
            lines, start_line = inspect.getsourcelines(func)
            whitespace = len(lines[0]) - len(lines[0].lstrip())
            for i, line in enumerate(lines):
                lines[i] = line[whitespace:]
            code = ''.join(lines).strip()

            if code in [m['code'] for m in method]:
                continue

            # Get the method arguments
            args, varargs, keywords, defaults = inspect.getargspec(func)
            arguments = inspect.formatargspec(args, varargs=varargs, varkw=keywords, defaults=defaults)

            method.append({
                'docstring': pydoc.getdoc(func),
                'defining_class': cls,
                'arguments': arguments,
                'code': code,
                'lines': {'start': start_line, 'total': len(lines)},
                'file': inspect.getsourcefile(func)
            })

    # sort attributes & methods
    data['attributes'] = collections.OrderedDict(sorted(data['attributes'].items()))
    data['methods'] = collections.OrderedDict(sorted(data['methods'].items(), key=lambda m: m[0].strip('__')))

    return data
