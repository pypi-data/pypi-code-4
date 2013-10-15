# -*- coding: utf-8 -*-

from .. import ValidationError

def _prehook(_value=None, *args, **kwargs):
	if type(_value) not in (dict, list, set, tuple):
		raise ValidationError('This validator requires a collection type [dict, list, set, tuple].')
	return _value


def drop_keys(keys=(), _value=None, *args, **kwargs):
	if type(_value) is not dict:
		raise ValidationError('This validator requires a dictionary.')
	[_value.pop(k, None) for k in keys]
	return _value

def contains(key, _value=None, *args, **kwargs):
	if not key in _value:
		raise ValidationError('The key %s was not found in the target collection.' % key)
	return _value