from numbers import Number

from .. import ValidationError


def _prehook(*args, **kwargs):
	value = kwargs.get('_value')

	if not isinstance(value, Number):
		raise ValidationError('This value must be a number.')

	return value

def range(low=None, high=None, *args, **kwargs):
	value = kwargs.get('_value')
	
	if low is not None and value < low:
		raise ValidationError('This number must be greater than or equal to %s' % low)

	if high is not None and value > high:
		raise ValidationError('This number must be less than or equal to %s' % high)

	return value

def minimum(number, *args, **kwargs):
	value = kwargs.get('_value')

	if value < number:
		raise ValidationError('This number must be greater than or equal to %s' % number)

	return value

def maximum(number, *args, **kwargs):
	value = kwargs.get('_value')

	if value > number:
		raise ValidationError('This number must be less than or equal to %s' % number)

	return value

def between(low=None, high=None, *args, **kwargs):
	value = kwargs.get('_value')

	if low is not None and value <= low:
		raise ValidationError('This number must be greater than %s' % low)

	if high is not None and value >= high:
		raise ValidationError('This number must be less than %s' % high)

	return value

def equal(number, *args, **kwargs):
	value = kwargs.get('_value')

	if value != number:
		raise ValidationError('This number must be equal to %s' % number)

	return value

def zero(*args, **kwargs):
	value = kwargs.get('_value')
	if value is not 0:
		raise ValidationError('This number must be zero.')
	return value