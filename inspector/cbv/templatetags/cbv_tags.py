from django import template

register = template.Library()


@register.filter
def namesake_methods(parent_klass, name):
    namesakes = [m for m in parent_klass.get_methods() if m.name == name]
    assert(namesakes)
    # Get the methods in order of the klasses
    try:
        result = [next((m for m in namesakes if m.klass == parent_klass))]
        namesakes.pop(namesakes.index(result[0]))
    except StopIteration:
        result = []
    for klass in parent_klass.get_all_ancestors():
        # Move the namesakes from the methods to the results
        try:
            method = next((m for m in namesakes if m.klass == klass))
            namesakes.pop(namesakes.index(method))
            result.append(method)
        except StopIteration:
            pass
    assert(not namesakes)
    return result
