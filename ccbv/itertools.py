from operator import itemgetter

import six


def group_by(iterable, key=None, keyval=None):
    """
    Builds up a lookup table, grouping the values from the iterable by the
    result of applying `key` to each item.

    For example:

    >>> group_by(['foo', 'bar', 'baz', 'qux', 'quux'], key=lambda s: s[0])
    {
        'b': ['bar', 'baz'],
        'f': ['foo'],
        'q': ['quux', 'qux']
    }

    For extra power, you can even change the values while building up the LUT.
    To do so, use the `keyval` function instead of the `key` arg:

    >>> group_by(['foo', 'bar', 'baz', 'qux', 'quux'],
    ...          keyval=lambda s: (s[0], s[1:].upper()))
    {
        'b': ['AR', 'AZ'],
        'f': ['OO'],
        'q': ['UX', 'UUX']
    }

    """
    if keyval is None:
        if key is None:
            raise ValueError("Expected either a `key` or `keyval` argument")
        else:
            if isinstance(key, six.string_types):
                key = itemgetter(key)
            keyval = lambda v: (key(v), v)  # noqa: E731

    lut = {}
    for value in iterable:
        k, v = keyval(value)
        try:
            s = lut[k]
        except KeyError:
            s = lut[k] = list()
        s.append(v)

    return lut


def mapv(d, mapper):
    """Run the given mapper on each value of the given dictionary."""
    return dict((k, mapper(v)) for k, v in six.iteritems(d))
