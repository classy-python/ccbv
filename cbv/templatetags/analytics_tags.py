from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('_analytics.html')
def analytics():
    return {
        'google_key': 'UA-29872137-1',
        'DEBUG': settings.DEBUG,
    }
