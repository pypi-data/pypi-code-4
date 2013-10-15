# -*- coding: utf-8 -*-

from .. import ValidationError


def boolean(_value=None, *args, **kwargs):
	return False if not _value else True

def strbool(_value=None, *args, **kwargs):
	false_list = [
		'false',
		'0'
	]

	return False if not _value or _value in false_list else True

def integer(_value=None, *args, **kwargs):
	try:
		return int(_value)
	except ValueError:
		raise ValidationError('The value %s cannot be converted to an integer.' % _value)

def longint(_value=None, *args, **kwargs):
	try:
		return long(_value)
	except ValueError:
		raise ValidationError('The value %s cannot be converted to a long integer.' % _value)

def numeric(_value=None, *args, **kwargs):
	if float(_value).is_integer():
		return int(_value)

	return float(_value)

def string(_value=None, *args, **kwargs):
	try:
		return unicode(_value)
	except ValueError:
		raise ValidationError('The specified value %s could not be casting to a unicode string' % _value)

# casts any "none type" value to None, else returns value unharmed. language agnostic.
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

	value = str(_value).lower().strip()
	
	return None if value in none_list else _value