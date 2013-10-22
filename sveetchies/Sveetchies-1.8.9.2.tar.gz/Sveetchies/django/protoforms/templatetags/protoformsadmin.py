# -*- coding: utf-8 -*-
from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='get_extension_value')
def get_extension_value(field_object=None):
    extension_fields_values = getattr(field_object.form, 'cf_extension_fields_values', False)
    if extension_fields_values and field_object.name in extension_fields_values:
        return mark_safe(u'<p><ins>Valeur manuelle supplémentaire:</ins> %s</p>' % extension_fields_values[field_object.name])
    return ''
