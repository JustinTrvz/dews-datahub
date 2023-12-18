from django import template

register = template.Library()

@register.filter(name='get_related')
def get_related(obj, attr):
    return getattr(obj, attr, None)
