from functools import partial
from inspect import getmembers

from filters import lookup

class ValidationError(Exception): pass

class Schema(object):

	def __init__(self, name):
		self._name = name
		self._fields = {}
		self._valid = False

	def __getattr__(self, attr):
		return self.add_field(attr, Field(self, attr))

	def __repr__(self):
		return '[Schema: %r] - [%r]' % (self.name, ', '.join([f for f in self._fields]))

	@property
	def name(self):
		return self._name

	@property
	def valid(self):
		return self._valid

	def add_field(self, name, field):
		self._fields[name] = field
		setattr(self, name, field)
		return field

	def validate(self, data_dict, **kwargs):
		self._valid = True
		for name, field in self._fields.iteritems():
			if not field.validate(data_dict.get(name)):
				self._valid = False

	def reset(self):
		[f.reset() for n, f in self._fields.iteritems()]
		self._valid = False
		
class Field(object):

	def __init__(self, schema, name):
		self._schema = schema
		self._name = name
		self._original_value = None
		self._value = None
		self._filters = []
		self._valid = False
		self._errors = []

		self._required = False
		self._alternate_name = None

		self._ran = False

	def __repr__(self):
		return '[Field: %r] - [%r, %r, %r] - %r' % (self.name, self._original_value, self._value, self._valid, self._errors)

	@property
	def name(self):
		return self._name

	@property
	def valid(self):
		return self._valid

	@property
	def errors(self):
		return self._errors

	@property
	def original(self):
		return self._original_value

	@property
	def result(self):
		return self._value

	def reset(self):
		self._ran = False
		self._valid = False
		self._errors = []
		self._original_value = self._value = None

	def validate(self, value):
		if self._ran:
			return

		self._original_value = self._value = value
		
		try:
			for f in self._filters:
				self._value = f.run(self._value)
		except ValidationError as e:
			self._valid = False
			self._errors.append(e.message)
		else:
			self._valid = True

		self._check_options()
		return self._valid

	def _check_options(self):
		if self._value is None and self._required:
			self._errors.append('This field is required.')
			self._valid = False

	def __call__(self, *args, **kwargs):
		option_alias_map = {
			'req': '_required',
			'alt': '_alternate_name',
		}
	
		for k, v in kwargs.iteritems():
			if k in option_alias_map:
				setattr(self, option_alias_map[k], v)

		if self._alternate_name:
			self._schema.add_field(self._alternate_name, self)

		return self

	def __getattr__(self, name):
		fxn, pre, post = lookup(name)
		if not fxn:
			raise RuntimeError('Filter %s is undefined' % name)
		
		if pre:
			pref = Filter(self, pre)
			self._filters.append(pref)

		f = Filter(self, fxn)
		self._filters.append(f)

		if post:
			postf = Filter(self, post)
			self._filters.append(postf)

		return f

class Filter(object):

	def __init__(self, field, fxn):
		self._field = field
		self._validation_fxn = fxn

	def __call__(self, *args, **kwargs):
		partial_fxn = partial(self._validation_fxn, *args, **kwargs)
		partial_fxn.__name__ = self._validation_fxn.__name__
		self._validation_fxn = partial_fxn
		return self._field

	def __repr__(self):
		return '[Filter - %r]' % self._validation_fxn.__name__

	def run(self, value):
		processed = self._validation_fxn(_value=value)
		return processed