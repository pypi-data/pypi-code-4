import re

from .. import ValidationError

_regexes = {
	'word_notword_spaces': re.compile(r'[\w\W\s]*', re.IGNORECASE),
	'notword': re.compile(r'\W', re.IGNORECASE),
	'punctuation': re.compile(r'[^\s\w\-]+', re.IGNORECASE),
	'alphanumeric': re.compile(r'[a-z\s\-_0-9]*', re.IGNORECASE),
	'alpha': re.compile(r'[a-z\s\-_]*', re.IGNORECASE),
	'numeric': re.compile(r'\d*', re.IGNORECASE),
	'dash_under_space': re.compile (r'[\-_\s]+', re.IGNORECASE)
}

def _prehook(*args, **kwargs):
	value = kwargs.get('_value')

	if type(value) not in (unicode, str):
		raise ValidationError('This value must be a str or unicode type.')

	return value if type(value) is unicode else unicode(value)

def text(min_len=None, max_len=None, *args, **kwargs):
	value = kwargs.get('_value')

	if min_len is not None and len(value) <= min_len:
		raise ValidationError('Text length must be greater than %s' % min_len)

	if max_len is not None and len(value) >= max_len:
		raise ValidationError('Text length must be less than %s' % max_len)

	return value

def alphanumeric(*args, **kwargs):
	value = kwargs.get('_value')

	if not _regexes['alphanumeric'].match(value):
		raise ValidationError('This value must contain alphanumeric characters only.')

	return value

alnum = alphanumeric

def alpha(*args, **kwargs):
	value = kwargs.get('_value')

	if not _regexes['alpha'].match(value):
		raise ValidationError('This value must contain alphabetical characters only.')

	return value

def numeric(*args, **kwargs):
	value = kwargs.get('_value')

	if not _regexes['numeric'].match(value):
		raise ValidationError('This value must contain numeric characters only.')

	return value

def nonblank(*args, **kwargs):
	value = kwargs.get('_value')

	if len(value) <= 0:
		raise ValidationError('This value must not be empty.')

	return value

def removespaces(*args, **kwargs):
	return kwargs.get('_value').replace(u' ', u'')

def strip(*args, **kwargs):
	return kwargs.get('_value').strip()

def lower(*args, **kwargs):
	return kwargs.get('_value').lower()

def upper(*args, **kwargs):
	return kwargs.get('_value').upper()

def regex(regex, case=False, *args, **kwargs):
	value = kwargs.get('_value')

	if kwargs.get('case'):
		regex = re.compile(regex)
	else:
		regex = re.compile(regex, re.IGNORECASE)

	if not regex.match(value):
		raise ValidationError('The value must match the regex %s' % regex)

	return value

def canonize(*args, **kwargs):
	return _regexes['dash_under_space'].sub('_', kwargs.get('_value').strip().lower())

def slugify(*args, **kwargs):
	value = kwargs.get('_value')
	value = _regexes['punctuation'].sub('', value)
	value = _regexes['notword'].sub('-', value)
	return value.lower()