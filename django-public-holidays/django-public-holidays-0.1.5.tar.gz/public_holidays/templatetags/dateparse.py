import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def dateparse(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()