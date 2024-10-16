from django import template

register = template.Library()

@register.simple_tag
def make_list(n):
    return range(n)

@register.filter
def to(value):
    return range(value)

@register.filter
def range_filter(value):
    return range(value)