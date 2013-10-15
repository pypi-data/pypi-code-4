# -*- coding: utf-8 -*-

from functools import partial, wraps
from inspect import getmembers

from filters import lookup

class ValidationError(Exception): pass

from filters.casting import none

def _field_option(option_name):
	def _decorator(f):
		@wraps(f)
		def _wrapper(*args, **kwargs):
			self, field_names = args[0], args[1]
			
			if self._field_options[option_name] is not None:
				self._field_options[option_name] = None
				
				fields = []
				field_groups = []

				args = list(args)
				if option_name == 'match':
					for g in field_names:
						field_groups.append(self._get_fields_by_name(g))
					args.append(field_groups)
				else:
					if type(field_names) is list:
						fields = self._get_fields_by_name(field_names)
					elif field_names == 'all':
						fields = self._fields.values()
					args.append(fields)
				args = tuple(args)
				return f(*args, **kwargs)
			return None
		return _wrapper
	return _decorator


class Schema(object):

	def __init__(self, name=None, match=[], require=[], blank=[], extra='ignore'):
		self._name = name
		self._fields = {}
		self._extra = extra
		self._missing = []

		self._field_options = {}
		self._field_options['match'] = match
		self._field_options['require'] = require
		self._field_options['blank'] = blank

	def __getattr__(self, attr):
		return self.add_field(attr, Field(self, attr))

	def __repr__(self):
		return '[Schema: %r] - [%r]' % (self.name, ', '.join([repr(field) for name, field in self._fields.iteritems()]))

	''' returns a set of fields because alt names will return the same field '''
	def _get_fields_by_name(self, field_names):
		fields = []
		for f_name in field_names:
			try:
				fields.append(self._fields[f_name])
			except KeyError: pass
		return set(fields)

	@property
	def name(self):
		return self._name

	@property
	def errors(self):
		return {f.name: f.errors for f_name, f in self._fields.iteritems()}

	@property
	def valid(self):
		return all([f.valid for name, f in self._fields.iteritems()])

	@property
	def missing(self):
		return list(self._missing)

	def add_field(self, name, field):
		self._fields[name] = field
		setattr(self, name, field)
		return field

	@_field_option('require')
	def required_fields(self, field_names, fields):
		[f.require(True) for f in fields]

	def optional_fields(self, field_names):
		fields = self._get_fields_by_name(field_names)
		[f.require(False) for f in fields]

	@_field_option('blank')
	def blank_fields(self, field_names, fields):
		[f.blank(True) for f in fields]

	def not_blank_fields(self, field_names):
		fields = self._get_fields_by_name(field_names)
		[f.blank(False) for f in fields]
		
	@_field_option('match')
	def match_fields(self, field_names, field_groups):
		for group in field_groups:
			for f in group:
				others = group.copy()
				others.discard(f)
				f.match(*others)

	def validate(self, data_dict, **kwargs):
		supplied_fields = set(data_dict.keys())
		actual_fields = set(self._fields.keys())
		known_fields = supplied_fields.intersection(actual_fields)
		unknown_fields = supplied_fields.difference(actual_fields)
	
		if self._extra == 'ignore':
			data_dict = {k: data_dict[k] for k in known_fields}

		self.required_fields(self._field_options['require'])
		self.blank_fields(self._field_options['blank'])
		self.match_fields(self._field_options['match'])

		self._validate_required(data_dict)
		self._validate_blank(data_dict)
		self._validate_matching(data_dict)

		[field.validate(data_dict.get(f_name)) for f_name, field in self._fields.iteritems()]
			
	def _validate_required(self, data_dict):
		required_fields = set([f.name for f_name, f in self._fields.iteritems() if f.required])
		supplied_fields = set(data_dict.keys())

		missing_fields = required_fields - supplied_fields
		
		for f_name in missing_fields:
			field = self._fields[f_name]
			field._ran = True
			field._errors.append('This field cannot be missing.')

		return not missing_fields

	def _validate_blank(self, data_dict):
		for f_name, value in data_dict.iteritems():
			field = self._fields[f_name]
			if not field.blank_allowed and none(value) is None:
				field._ran = True
				field._errors.append('This field cannot be blank.')

	def _validate_matching(self, data_dict):
		for f_name, value in data_dict.iteritems():
			field = self._fields[f_name]
			must_match = field.must_match
	
			if must_match and type(must_match[0]) is not Field:
				must_match = self._get_fields_by_name(must_match)

			if any([value != data_dict[m.name] for m in must_match]):
				for m in must_match:
					m._ran = True
				field._ran = True
				field._errors.append('This field must match: [%s]' % ', '.join([m.name for m in must_match]))
			
	def reset(self):
		[f.reset() for n, f in self._fields.iteritems()]
		
class Field(object):

	def __init__(self, schema, name):
		self._schema = schema
		self._name = name
		self._filters = []
		self._required = None
		self._blank = None
		self._alternate_name = None
		self._match = []

		self.reset()

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

	@property
	def required(self):
		if self._required is None:
			return False
		return self._required

	@property
	def blank_allowed(self):
		if self._blank is None:
			return False
		return self._blank

	@property
	def must_match(self):
		return self._match

	def reset(self):
		self._ran = False
		self._valid = False
		self._errors = []
		self._original_value = self._value = None

	def validate(self, value):
		if self._ran:
			return self._valid

		self._original_value = self._value = none(_value=value)
		try:
			for f in self._filters:
				self._value = f.run(self._value)
		except ValidationError as e:
			self._valid = False
			self._errors.append(e.message)
		else:
			self._valid = True

		return self._valid

	def require(self, value=True):
		if self._required is None:
			self._required = value
		return self

	def blank(self, value=True):
		if self._blank is None:
			self._blank = value
		return self

	def match(self, *fields):
		if not self._match:
			self._match = fields
		return self
	
	def alt(self, alt_name):
		self._schema.add_field(alt_name, self)
		return self

	def __call__(self, *args, **kwargs):
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