import collections
import inspect
import pydoc

from .utils import get_mro


class LazyAttribute(object):
    functions = {
        'gettext': 'gettext_lazy',
        'reverse': 'reverse_lazy',
        'ugettext': 'ugettext_lazy',
    }

    def __init__(self, promise):
        func, self.args, self.kwargs, _ = promise.__reduce__()[1]
        try:
            self.lazy_func = self.functions[func.func_name]
        except KeyError:
            raise ImproperlyConfigured("'{}' not in known lazily called functions".format(func.func_name))

    def __repr__(self):
        arguments = []
        for arg in self.args:
            if isinstance(arg, basestring):
                arguments.append("'{}'".format(arg))
            else:
                arguments.append(arg)
        for key, value in self.kwargs:
            if isinstance(key, basestring):
                key = "'{}'".format(key)
            if isinstance(value, basestring):
                value = "'{}'".format(value)
            arguments.append("{}: {}".format(key, value))
        return '{func}({arguments})'.format(func=self.lazy_func, arguments=', '.join(arguments))


def is_secondary(name):
    return (
        name.startswith('Base')
        or name.endswith(('Base', 'Error', 'Mixin'))
        or name == 'ProcessFormView'
    )


def member_filter(member):
    whitelist = [
        '__init__',
        '__repr__',
    ]
    name = member[0]
    return name in whitelist or not name.startswith('__')


def build(thing, version):
    """Build a dictionary mapping of a class."""
    # import Promise so we can identify lazy function calls
    from django.utils.functional import Promise

    klass, name = pydoc.resolve(thing, forceload=0)
    mro = list(reversed(get_mro(klass)))

    try:
        _, start_line = inspect.getsourcelines(klass)
    except IOError:
        # inspect couldn't find the source code
        # 1.5's wizard views reference a NewBase class that causes this
        source_url = ''
    else:
        source_url = 'https://github.com/django/django/blob/{version}/{module_path}.py#L{line}'.format(
            line=start_line,
            module_path=klass.__module__.replace('.', '/'),
            version=version,
        )

    data = {
        'ancestors': collections.OrderedDict([(k.__name__, k.__module__) for k in mro[:-1]]),
        'attributes': collections.defaultdict(list),
        'docstring': pydoc.getdoc(klass),
        'is_secondary': is_secondary(name),
        'methods': collections.defaultdict(list),
        'module': klass.__module__,
        'name': name,
        'parents': inspect.getclasstree([klass])[-1][0][1],
        'source_url': source_url,
    }

    for cls in mro:
        members = filter(member_filter, inspect.getmembers(cls))
        methods = filter(lambda m: inspect.ismethod(m[1]), members)
        attributes = filter(lambda m: not inspect.isroutine(m[1]), members)

        # ATTRIBUTES
        for name, obj in attributes:
            attr = data['attributes'][name]

            # Replace lazy function call with an object representing it
            if isinstance(obj, Promise):
                obj = LazyAttribute(obj)

            if isinstance(obj, unicode):
                obj = "'{}'".format(obj)

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
