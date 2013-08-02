from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe

register = template.Library()


def js_bool(value):
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    return 'undefined'


def js_string(value):
    return mark_safe('"' + escapejs(value) + '"')


def jq_id(value):
    return mark_safe('"#' + escapejs(value) + '"')


def js_array(value):
    value = list(value)
    return mark_safe(str(value))


register.filter('js_string', js_string)
register.filter('jq_id', jq_id)
register.filter('js_array', js_array)
register.filter('js_bool', js_bool)