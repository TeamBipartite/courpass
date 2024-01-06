from django import template
register = template.Library()

@register.filter
def index(indexable, idx):
    return indexable[idx]