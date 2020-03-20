from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def divide(a, b):
    if b !=0:
        return round(float(a)/float(b), 2)
    else:
        return 0