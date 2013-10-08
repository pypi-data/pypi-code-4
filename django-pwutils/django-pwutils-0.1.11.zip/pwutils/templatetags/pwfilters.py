# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


@register.filter
def hash(context, key):
    return context[key]


@register.filter
def startswith(value, arg):
    """Usage, {% if value|starts_with:"arg" %}"""
    return value.startswith(arg)


@register.filter
def in_list(value, arg):
    return value in arg


@register.filter
def not_none(value):
    if value is None:
        return ''
    return value


@register.filter
def split(value, arg):
    return value.split(arg)[-1]


@register.filter
def split_str(value, arg):
    return value.split(arg)


@register.filter
def flatten(value):
    return u' '.join(value.split())
