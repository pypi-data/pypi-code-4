# -*- coding: utf-8 -*-

from valhalla import ValidationError


def _prehook(_value=None, *args, **kwargs):
    if type(_value) not in (dict, list, set, tuple):
        raise ValidationError(
            'This validator requires a collection type [dict, list, set, tuple].')
    return _value


def drop_keys(*args, **kwargs):
    _value = kwargs.pop('_value')

    if type(_value) is not dict:
        raise ValidationError('This validator requires a dictionary.')
    [_value.pop(unicode(k), None) for k in args]
    return _value


def contains(*args, **kwargs):
    _value = kwargs.pop('_value')
    for k in args:
        if k not in _value:
            raise ValidationError(
                'The key %s was not found in the target collection.' % k)
    return _value
