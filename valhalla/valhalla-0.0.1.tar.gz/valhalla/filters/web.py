import re

from . import strings
from .. import ValidationError

_regexes = {
	'email_address': re.compile(r'^[a-z0-9\._\+%-]+@[a-z0-9\.-]+(\.[A-Z]{2,4})+$', re.IGNORECASE),
	'ipv4': re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$')
}

# debating breaking ALL inter-module dependencies, 
# including this seemingly innocuous reference.
def _prehook(*args, **kwargs):
	return strings._prehook(_value=kwargs.get('_value'))

def email(*args, **kwargs):
	value = kwargs.get('_value')
	if not _regexes['email_address'].match(value):
		raise ValidationError('This value must be a valid email address.')
	return value

def ipv4(*args, **kwargs):
	value = kwargs.get('_value')
	if not _regexes['ipv4'].match(value):
		raise ValidationError('This value must be a valid IPV4 address.')
	return value