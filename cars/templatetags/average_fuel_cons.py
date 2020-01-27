from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def average_fuel_cons(l, km):
    return round(l/km*100, 2)