# -*- coding: utf-8 -*-

import re

from . import strings
from .. import ValidationError

_regexes = {
	'email_address': re.compile(r'^[a-z0-9\._\+%-]+@[a-z0-9\.-]+(\.[A-Z]{2,4})+$', re.IGNORECASE),
	'ipv4': re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'),
	'url': re.compile(r'')
}

# debating breaking ALL inter-module dependencies, 
# including this seemingly innocuous reference.
def _prehook(*args, **kwargs):
	return strings._prehook(_value=kwargs.get('_value'))

def email(_value=None, *args, **kwargs):
	if not _regexes['email_address'].match(_value):
		raise ValidationError('This value must be a valid email address.')
	return _value

def ipv4(_value=None, *args, **kwargs):
	if not _regexes['ipv4'].match(_value):
		raise ValidationError('This value must be a valid IPV4 address.')

	if filter(lambda x: int(x) > 255, _value.split('.')):
		raise ValidationError('Octets may not exceed 255.')

	return _value

def cidr4(_value=None, *args, **kwargs): pass
def cidr6(_value=None, *args, **kwargs): pass
def macaddress(_value=None, *args, **kwargs): pass

# this is really just a shortcut for uri(schemes=['http', 'https'])
def url(scheme=False, tld=True, qs=True, frag=True, _value=None, *args, **kwargs): pass

# will implement this when I feel like pasting in a giant list of registered schemes...
def uri(schemes=[], _value=None, *args, **kwargs): pass
