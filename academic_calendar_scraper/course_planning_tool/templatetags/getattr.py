from django import template
register = template.Library()

@register.filter
def getattr(obj, attribute):
    """ Try to get an attribute from an object.
    """
    return obj.__getattribute__(attribute)