from django import template
from cbv.models import Klass, Module, ProjectVersion

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


@register.inclusion_tag('cbv/includes/breadcrumb.html')
def breadcrumb(obj, others=None, final=False):
    return {
        'object': obj,
        'others': others,
        'final': final,
    }


@register.inclusion_tag('cbv/includes/breadcrumbs.html')
def breadcrumbs(version, module=None, klass=None):
    other_versions = ProjectVersion.objects.filter(project=version.project).exclude(pk=version.pk)
    final = version
    context = {
        'version': version,
        'other_versions': other_versions
    }

    if module:
        other_modules = Module.objects.filter(project_version=version).exclude(pk=module.pk)
        context.update({
            'module': module,
            'other_modules': other_modules
        })
        final = module

        if klass:
            other_klasses = Klass.objects.filter(module=module).exclude(pk=klass.pk)
            context.update({
                'klass': klass,
                'other_klasses': other_klasses
            })
            final = klass

    context['final'] = final
    return context


@register.filter
def is_final(obj, last):
    return obj == last
