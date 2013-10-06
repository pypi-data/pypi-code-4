from .. import ValidationError


def boolean(_value=None, *args, **kwargs):
	if not _value:
		return False
	
	return True

def jsbool(_value=None, *args, **kwargs):
	false_list = [
		'undefined',
		'false',
		'null',
		'[]',
		'{}'
	]

	if not _value or _value in false_list:
		return False
	
	return True

def strbool(_value=None, *args, **kwargs):
	false_list = [
		'undefined',
		'false',
		'0',
		'[]',
		'{}',
		'',
		'None',	
	]

	if not _value or _value in false_list:
		return False

	return True

def integer(_value=None, *args, **kwargs):
	try:
		return int(_value)
	except ValueError:
		raise ValidationError('The value %s cannot be converted to an integer.' % _value)

def longint(_value=None, *args, **kwargs):
	try:
		return long(_value)
	except ValueError:
		raise ValidationError('The value %s cannot be converted to an integer.' % _value)

def numeric(_value=None, *args, **kwargs):
	if float(_value).is_integer():
		return int(_value)

	return float(_value)

def string(_value=None, *args, **kwargs):
	try:
		return unicode(_value)
	except ValueError:
		raise ValidationError('The specified value %s could not be casting to a unicode string' % _value)