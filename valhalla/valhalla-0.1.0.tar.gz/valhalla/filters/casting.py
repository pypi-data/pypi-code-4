# -*- coding: utf-8 -*-

from decimal import Decimal, InvalidOperation
from valhalla import ValidationError


def boolean(_value=None, *args, **kwargs):
    return False if not _value else True


def strbool(_value=None, *args, **kwargs):
    false_list = [
        'false',
        '0'
    ]

    _value = none(_value=_value)

    if not _value:
        return False

    if _value in false_list:
        return False

    return True


def integer(_value=None, *args, **kwargs):
    try:
        return int(_value)
    except (ValueError, TypeError):
        raise ValidationError(
            'The value %s cannot be converted to \
            an integer.' % _value)


def longint(_value=None, *args, **kwargs):
    try:
        return long(_value)
    except ValueError:
        raise ValidationError(
            'The value %s cannot be converted \
            to a long integer.' % _value)


def numeric(_value=None, *args, **kwargs):
    if float(_value).is_integer():
        return int(_value)

    return float(_value)


def decimal(_value=None, *args, **kwargs):
    try:
        return Decimal(_value)
    except (ValueError, InvalidOperation):
        raise ValidationError(
            'The specified value %s could not \
            be casted to a Decimal' % _value)


def string(_value=None, *args, **kwargs):
    try:
        return unicode(_value)
    except ValueError:
        raise ValidationError(
            'The specified value %s could not be \
            casted to a unicode string' % _value)


def none(_value=None, *args, **kwargs):
    none_list = [
        '',
        'none',
        'undefined',
        'null',
        'n/a',
        'na',
        '[]',
        '{}',
    ]

    string_value = unicode(_value).lower().strip()

    return None if string_value in none_list else _value
