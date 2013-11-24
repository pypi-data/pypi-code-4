# -*- coding: utf-8 -*-

"""Templatetags."""

from django import template
from django.forms.forms import BoundField

from ui_permissions.descriptor.resource import Resource


def query(resource_desc, component_type_name, name, state_name):
    """Builds and returns result of query on given resource description object.

    :param resource_desc: recourse description object
    :type resource_desc: ui_permissions.descriptor.resource.Resource
    :param component_type_name: field or element
    :type component_type_name: str
    :param name: resource name
    :type name: str
    :param state_name: component state name
    :type state_name: str
    :returns: check result
    :rtype: bool

    """
    if not isinstance(resource_desc, Resource):
        raise TypeError('Filter operates on non-Resource instance')
    component_type = getattr(resource_desc, component_type_name)
    component = getattr(component_type, name)
    return getattr(component, state_name)


register = template.Library()


@register.filter
def element_VISIBLE(resource_desc, arg):
    """Checks if field is visible."""
    return query(resource_desc, 'element', arg, 'VISIBLE')


@register.filter
def element_HIDDEN(resource_desc, arg):
    """Checks if field is hidden."""
    return query(resource_desc, 'element', arg, 'HIDDEN')


@register.filter
def field_EDITABLE(resource_desc, arg):
    """Checks if field is editable."""
    if isinstance(arg, BoundField):
        name = arg.name
    else:
        name = arg
    return query(resource_desc, 'field', name, 'EDITABLE')


@register.filter
def field_DISABLED(resource_desc, arg):
    """Checks if field is disabled."""
    if isinstance(arg, BoundField):
        name = arg.name
    else:
        name = arg
    return query(resource_desc, 'field', name, 'DISABLED')


@register.filter
def field_HIDDEN(resource_desc, arg):
    """Checks if field is disabled."""
    if isinstance(arg, BoundField):
        name = arg.name
    else:
        name = arg
    return query(resource_desc, 'field', name, 'HIDDEN')
