# -*- coding: utf-8 -*-

from numbers import Number

from .. import ValidationError


def _prehook(_value=None, *args, **kwargs):
    if not isinstance(_value, Number):
        raise ValidationError('This _value must be a number.')

    return _value


def range(low=None, high=None, _value=None, *args, **kwargs):
    if low is not None and _value < low:
        raise ValidationError(
            'This number must be greater than or equal to %s' % low)

    if high is not None and _value > high:
        raise ValidationError(
            'This number must be less than or equal to %s' % high)

    return _value


def minimum(number, _value=None, *args, **kwargs):
    if _value < number:
        raise ValidationError(
            'This number must be greater than or equal to %s' % number)

    return _value


def maximum(number, _value=None, *args, **kwargs):
    if _value > number:
        raise ValidationError(
            'This number must be less than or equal to %s' % number)

    return _value


def between(low=None, high=None, _value=None, *args, **kwargs):
    if low is not None and _value <= low:
        raise ValidationError('This number must be greater than %s' % low)

    if high is not None and _value >= high:
        raise ValidationError('This number must be less than %s' % high)

    return _value


def equal(number, _value=None, *args, **kwargs):
    if _value != number:
        raise ValidationError('This number must be equal to %s' % number)

    return _value


def zero(_value=None, *args, **kwargs):
    if _value is not 0:
        raise ValidationError('This number must be zero.')
    return _value
