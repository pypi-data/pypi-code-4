"""
	Interfacing with the results of an FMXML query
	
	Copyright (c) 2012, Mel Collins <mel@raumkraut.net>
	Released under the terms of the X11/MIT License
	(see included LICENSE file)
"""
import re
import collections
import urlparse
from StringIO import StringIO
from xml.etree import ElementTree as ET

from . import exceptions
from . import query


class FMResultSet(object):
	"""
		Base class for query results.
		
		Common end-developer functionality:
			__iter__: Iterate over the result data
			fields: Dict of field information
			__len__: The number of results in this set
			count: See __len__ ^
			total: The total number of results, without limits applied
			error: Error code (if any)
	"""
	# Assumed charset for XML
	_CHARSET = 'utf8'
	
	def __init__(self, data=None, grammar=None, server=None, db=None, layout=None, **kwargs):
		super(FMResultSet, self).__init__(**kwargs)
		self._grammar_class = grammar or FMResultSetGrammar
		self._server = server
		self._db = db
		self._layout = layout
		self._xml = None
		self._grammar = None
		self.database = None
		self.layout = None
		self.fields = None
		self.count = None
		self.total = None
		self.error = None
		if data:
			self.parse(data)
		
	@property
	def grammar(self):
		""" Names the grammar used for parsing the result data. """
		return self._grammar.GRAMMAR
		
	def __iter__(self):
		""" Yields FMRecord instances. """
		fields = list(self._grammar.fields)
		for record in self._grammar.records:
			data = {}
			for idx, field in enumerate(fields):
				val = self._grammar.convert(record['data'][idx], field['type'])
				## Is it good to be special-casing 'container' here,
				## and not handling it as part of the grammar's convert()?
				if field['type'] == 'container':
					data[field['id']] = FMContainer(val, server=self._server)
				else:
					data[field['id']] = val
				
			yield FMRecord(
					id=record['id'],
					mod_id=record['mod-id'],
					params=data,
					layout=self._layout,
					)
			
		
	def __len__(self):
		return self.count or 0
		
	def __getitem__(self, idx):
		if not isinstance(idx, (int, long)):
			raise TypeError('{cls} indexes must be integers, not {typ}'.format(
					cls=self.__class__.__name__,
					typ=type(idx).__name__,
					))
		
		iterator = iter(self)
		try:
			for i in range(idx):
				iterator.next()
			return iterator.next()
		except StopIteration:
			raise IndexError('{0} index out of range'.format(self.__class__.__name__))
		
	def parse(self, data):
		"""
			Parse the given `data` string or file-like object.
			
			Returns the parsed XML structure (ElementTree), as well as
			populating various object attributes.
		"""
		if hasattr(data, 'read'):
			xml = ET.parse(data).getroot()
		else:
			# ET.fromstring doesn't accept unicode -_-
			if isinstance(data, unicode):
				data = data.encode(self._CHARSET)
			xml = ET.fromstring(data)
		self._xml = xml
		self._grammar = self._grammar_class(xml)
		
		self.database = self._grammar.database
		self.layout = self._grammar.layout
		self.fields = dict((g['id'], g) for g in self._grammar.fields)
		self.count = self._grammar.count
		self.total = self._grammar.total
		self.error = self._grammar.error
		return xml
		
	

class FMGrammar(object):
	"""
		Base class for grammar parsers.
		
		Grammar parsers restrict themselves to extracting information
		from an XML document, and serving it up in the manner expected
		by FMResultSet.
	"""
	GRAMMAR = None
	NAMESPACE = None
	# These are used to convert() values into Python types
	# CONVERTERS convert FMXML field-types to Python-types
	# DEFAULT_CONVERTER is a key in the CONVERTERS dict
	CONVERTERS = {}
	DEFAULT_CONVERTER = None
	
	"""
		Methods/properties to be implemented by subclasses
	"""
	@property
	def database(self):
		"""
			Returns the name of the database in the given `xml`.
		"""
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def layout(self):
		"""
			Returns the name of the layout in the given `xml`.
		"""
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def fields(self):
		"""
			Yields dictionaries of field data for the given `xml`.
			
			The resultant dictionaries should have:
				id: The layout-unique field ID
				type: The FM field-type
		"""
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def records(self):
		"""
			Yields dictionaries of record info for the given `xml`.
			
			The yielded dictionaries should have:
				id: The "record-id" of the record
				mod-id: The "mod-id" of the record (tracks changes)
				data: [List of field-data; MUST be in the same order
					as returned by the `fields` property]
		"""
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def count(self):
		""" Returns the number of records present. """
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def total(self):
		""" Returns the number of records should there be no limits. """
		raise NotImplementedError('To be implemented by subclasses')
	@property
	def error(self):
		""" Returns the error code. """
		raise NotImplementedError('To be implemented by subclasses')
	
	"""
		Methods which shouldn't need to be altered by subclasses.
	"""
	def __init__(self, xml, **kwargs):
		super(FMGrammar, self).__init__(**kwargs)
		self.root = xml
		
	def __repr__(self):
		return '<{mod}.{cls} {grammar}>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__.__name__,
				grammar=self.GRAMMAR,
				)
	
	def ns(self, path):
		"""
			Applies this grammar's namespace to the given xpath string.
		"""
		return re.sub(
				r'/(?=[A-z0-9])',
				r'/{{{0}}}'.format(self.NAMESPACE),
				path,
				)
	
	def convert(self, value, type):
		"""
			Converts the given string `value` to a Python-native type.
			
			The supplied `type` indicates the nature of the `value`, so
			determines how it is converted.
		"""
		func = self.CONVERTERS.get(type, None)
		if func is None:
			func = self.CONVERTERS.get(self.DEFAULT_CONVERTER)
		return func(value)
		
	

class FMResultSetGrammar(FMGrammar):
	"""
		Class for processing the "fmresultset" XML grammar.
	"""
	GRAMMAR = 'fmresultset'
	NAMESPACE = 'http://www.filemaker.com/xml/fmresultset'
	CONVERTERS = {
			'number': lambda x: int(x) if x and x.isdigit() else None,
			'text': lambda x: unicode(x) if x else u'',
			}
	DEFAULT_CONVERTER = 'text'
	
	@property
	def database(self):
		ds = self.root.find(self.ns('./datasource'))
		return ds.get('database')
	@property
	def layout(self):
		ds = self.root.find(self.ns('./datasource'))
		return ds.get('layout')
	@property
	def fields(self):
		for elem in self.root.findall(self.ns('./metadata/field-definition')):
			yield {
					'id': elem.get('name'),
					'type': elem.get('result'),
					}
	@property
	def records(self):
		for elem in self.root.findall(self.ns('./resultset/record')):
			data = []
			for field in elem.findall(self.ns('./field')):
				# Not every <field> contains a <data>
				field_data = field.find(self.ns('./data'))
				if field_data is not None:
					data.append(field_data.text)
				else:
					data.append(None)
			yield {
					'id': int(elem.get('record-id'), 10),
					'mod-id': int(elem.get('mod-id'), 10),
					'data': data,
					}
	@property
	def count(self):
		return int(self.root.find(self.ns('./resultset')).get('fetch-size'))
	@property
	def total(self):
		return int(self.root.find(self.ns('./resultset')).get('count'))
	@property
	def error(self):
		return int(self.root.find(self.ns('./error')).get('code'))
	

class FMRecord(collections.MutableMapping):
	"""
		Represents a single record in a result set.
		
		Acts like a dict for most purposes.
		
		Should not need to be instantiated directly.
	"""
	def __init__(self, id, mod_id, params, layout=None, **kwargs):
		super(FMRecord, self).__init__(**kwargs)
		self.id = id
		self._mod_id = mod_id
		self._layout = layout
		self._params = params
		self._old_values = {}
		
	def __repr__(self):
		return '<{mod}.{cls} {id}@{mod_id}>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__.__name__,
				id=self.id,
				mod_id=self._mod_id,
				)
	
	def __len__(self):
		return len(self._params)
	def __iter__(self):
		return self._params.__iter__()
	def __getitem__(self, key):
		return self._params[key]
	def __setitem__(self, key, val):
		if key not in self._params:
			raise KeyError('{cls} has no such field: {key!r}'.format(cls=self.__class__.__name__, key=key))
		
		self._old_values.setdefault(key, self._params[key])
		self._params[key] = val
		
	def __delitem__(self, key):
		raise exceptions.FMNotSupportedError('Cannot delete {0} fields'.format(self.__class__.__name__))
		
	
	def save(self):
		"""
			Save any changes made to this record to the database.
			
			Returns False if there are no changes, True otherwise.
		"""
		if self._layout is None:
			raise exceptions.FMNotSupportedError('Cannot edit database metadata records')
		
		changes = {}
		for field, old_val in self._old_values.items():
			new_val = self._params[field]
			if new_val != old_val:
				changes[field] = new_val
		if not changes:
			return False
		
		new_record = self._layout.edit(self.id, **changes)
		self._mod_id = new_record._mod_id
		self._old_values = {}
		## TODO: Should we return the new_record instead?
		return True
		
	def duplicate(self):
		"""
			Duplicate this record in the database.
			
			This will not work if the record contains any non-incrementing
			unique keys.
			
			Returns the new record.
		"""
		if self._layout is None:
			# Most likely not a real record
			raise exceptions.FMNotSupportedError('Cannot duplicate database metadata records')
		return self._layout.duplicate(self.id)
		
	def delete(self):
		"""
			Delete this record from the database.
			
			Returns True if the record was deleted, False if there was
			nothing to delete in the first place.
		"""
		if self._layout is None:
			# This probably isn't actually a record; it's some metadata
			raise exceptions.FMNotSupportedError('Cannot delete database metadata records')
		return self._layout.delete(self.id)
		
	

class FMContainer(object):
	"""
		Wraps binary data referenced in a record.
		
		Acts somewhat like a file-like object.
		
		Should not need to be instantiated directly.
	"""
	def __init__(self, url, server, db=None, **kwargs):
		super(FMContainer, self).__init__(**kwargs)
		self._server = server
		self._db = None
		# Extract info from the URL
		## Seems kinda silly splitting a URL apart, just to reconstruct it :/
		path, params = url.split('?', 1)
		path, extension = path.rsplit('.', 1)
		params = urlparse.parse_qs(params)
		self._query = query.FMBinaryQuery(
				db=self._db or params['-db'][0],
				layout=params['-lay'][0],
				id=params['-recid'][0],
				field=params['-field'][0],
				type=extension,
				)
		self._data = None
		self.url = None
		
	def __repr__(self):
		return '<{cls} {url!r}>'.format(
				cls=self.__class__.__name__,
				url=self._query,
				)
		
	
	# Defer certain methods to lazily-fetched data
	@property
	def read(self, *args, **kwargs):
		if self._data is None:
			## TODO: Use prefetch/stream parameter (once it works)
			response = self._server._request(self._query)
			self.url = response.url
			self._data = StringIO(response.content)
		return self._data.read
		
	
