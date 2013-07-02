"""
	Compiling and manipulating queries to the server.
	
	Copyright (c) 2012, Mel Collins <mel@raumkraut.net>
	Released under the terms of the X11/MIT License
	(see included LICENSE file)
"""
import re
import urllib

from . import exceptions

ASC = 'ascend'
DESC = 'descend'


class FMQuery(object):
	"""
		Used to compile and manipulate queries on a server.
		
		All query-altering methods should also return `self`, so as to
		permit method chaining.
		
		Should usually not need be instantiated directly, but through
		a FMServer interface.
	"""
	method = 'GET'
	grammar = 'fmresultset.xml'
	
	def __init__(self, command=None, db=None, layout=None, server=None, **kwargs):
		"""
			Init a new FMQuery.
			
			Arguments (all optional, with various consequences):
				command: The string command the query shall perform.
				db: The database as a FMDatabase or string database name
				layout: The layout as a FMLayout or string layout name
				server: The FMServer instance the query belongs to
		"""
		super(FMQuery, self).__init__(**kwargs)
		
		# Used for execute(), should it be supplied
		self._server = server
		# The db can come in as an object, string, or None
		self._db = None
		self._db_id = None
		if hasattr(db, 'get_layout'):
			self._db = db
			self._db_id = db.id
		elif db is not None:
			if self._server:
				self._db = self._server.get_db(db)
			self._db_id = db
		# The layout can come in as an object, string or None, too
		self._layout = None
		self._layout_id = None
		if hasattr(layout, 'get_query'):
			self._layout = layout
			self._layout_id = layout.id
		elif layout is not None:
			if self._server:
				self._layout = self._server.get_layout(self._db_id, layout)
			self._layout_id = layout
		# Check for missing or conflicting database
		if self._layout:
			if self._db_id is None:
				self._db_id = self._layout.db.id
			elif self._layout.db.id != self._db_id:
				raise exceptions.FMNotSupportedError('{0} received conflicting database IDs: {1!r} != {2!r}'.format(self.__class__.__name__, self._layout.db.id, self._db_id))
		
		self.command = command
		self._reset_params()
		
	def __repr__(self):
		return '<{mod}.{cls} {id:x} command={cmd!r}>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__.__name__,
				id=id(self),
				cmd=self.command,
				)
		
	def __str__(self):
		return self.to_string()
		
	
	def _reset_params(self, **kwargs):
		"""
			Re-initalises the query params to defaults.
			
			Any supplied keyword arguments are also put into the params.
		"""
		## Dict, because FM ignores repeats of the same param anyway
		self._params = {}
		db = self._db_id
		if db:
			self._params['-db'] = db
		if self._layout_id:
			self._params['-lay'] = self._layout_id
		self._params.update(kwargs)
		
	def _normalise_field_params(self, params):
		"""
			Normalise the given field dict, and check for suitability.
			
			Raises an FMNotSupportedError if the params are unsuitable.
		"""
		norm = {}
		for key, val in params.items():
			if key.startswith('-'):
				raise exceptions.FMNotSupportedError('Field names cannot begin with "-"')
			## NB. The FileMaker docs say, for example:
			## "The period cannot be followed by the text string op
			## (the two letters "op"). For example, myfield.op is an
			## invalid field name."
			## But this leaves things like "myfield.option" a grey area...
			if '.op' in key:
				raise exceptions.FMNotSupportedError('Field names cannot contain ".op"')
			if '.global' in key:
				raise exceptions.FMNotSupportedError('Field names cannot contain ".global"')
			if re.search('\.[0-9]', key):
				raise exceptions.FMNotSupportedError('Field names cannot contain ".[0-9]"')
			
			norm[key] = val if val is not None else ''
		
		return norm
		
	
	def to_string(self):
		"""
			Compiles the query into a URL query-string.
		"""
		params = urllib.urlencode(self._params)
		if self.command:
			cmd = urllib.quote_plus(self.command)
			if params:
				params += '&-' + cmd
			else:
				params = '-' + cmd
		return params
		
	def to_dict(self):
		"""
			Returns a dictionary of query parameters suitable for use
			with the Requests library.
		"""
		params = {}
		# Convert values to strings. We don't have to (requests does
		# that for us), but we will anyway. Good idea? Not sure.
		for key, val in self._params.items():
			if not isinstance(val, basestring):
				val = str(val)
			params[key] = val
		if self.command:
			# This will include a "=", but that doesn't affect the results
			params['-' + self.command] = ''
		return params
		
	
	def execute(self):
		"""
			Perform the query on the server it was created from.
		"""
		if not self._server:
			raise exceptions.FMConnectionError('Cannot execute query: no server defined')
		return self._server.execute(self)
		
	
	def get(self, recid):
		"""
			Prep the query to fetch the given `recid`.
		"""
		self.command = 'find'
		self._reset_params()
		self._params['-recid'] = recid
		return self
		
	def duplicate(self, recid):
		"""
			Prep the query to duplicate the given `recid`.
		"""
		self.command = 'dup'
		self._reset_params()
		self._params['-recid'] = recid
		return self
		
	def delete(self, recid):
		"""
			Prep the query to delete the given `recid`.
		"""
		self.command = 'delete'
		self._reset_params()
		self._params['-recid'] = recid
		return self
		
	
class FMFindQuery(FMQuery):
	"""
		A special kind of Query for finding things.
		
		The functionality could be rolled into the standard FMQuery, and
		indeed it might, but there's enough find-specific functionality
		that a separate class doesn't seem like such a bad idea.
	"""
	ASC = ASC
	DESC = DESC
	_DEFAULT_COMMAND = 'findall'
	
	def __init__(self, db, layout, **kwargs):
		# The db and layout params are required, but just passed through
		super(FMFindQuery, self).__init__(command=self._DEFAULT_COMMAND, db=db, layout=layout, **kwargs)
		# Stores a cache of all the queried field-names
		self._fields = []
		
	
	def _convert_to_findquery(self):
		"""
			Convert existing find params to a compound-find
			
			Does nothing if we're already a 'findquery', and raises an
			FMNotSupportedError if we're not a 'find', otherwise.
		"""
		if self.command == 'findquery':
			return
		if self.command != 'find':
			raise exceptions.FMNotSupportedError('Cannot convert non-find to findquery')
		
		# Convert the fields to q#s
		fields = {}
		for key in self._fields:
			val = self._params.pop(key)
			op = self._params.pop(key + '.op', None)
			if op == 'neq' or val.startswith('^'):
				raise exceptions.FMNotSupportedError('Cannot compound not-equal comparison')
			fields[key] = val
		# Put them back in as findquery params
		self._fields = []
		self._add_query_fields(fields)
		
		lop = self._params.pop('-lop', None)
		if lop == 'or':
			# To each field, its own bracket
			compound = ';'.join('(q{0})'.format(i+1) for i in range(len(self._fields)))
		else:
			# All fields in one bracket
			compound = ','.join('q{0}'.format(i+1) for i in range(len(self._fields)))
			compound = '({0})'.format(compound)
		self._params['-query'] = compound
		self.command = 'findquery'
		
	def _add_query_fields(self, params):
		"""
			Adds the given dict to the Query as findquery params.
			
			Returns a list of the placeholder strings
		"""
		placeholders = []
		num_fields = len(self._fields)
		for i, key in enumerate(params):
			idx = i + num_fields + 1
			val = params[key]
			if hasattr(val, 'startswith') and val.startswith('^'):
				raise exceptions.FMNotSupportedError('Cannot use negation operator in compound queries')
			self._params['-q{0}'.format(idx)] = key
			self._params['-q{0}.value'.format(idx)] = val
			placeholders.append('q{0}'.format(idx))
			self._fields.append(key)
			
		
		return placeholders
	
	def find(self, **kwargs):
		"""
			Add a logical-and search to the query.
			
			Each keyword argument defines a key=value pair to search on.
			Each value should be a string, optionally including pattern-
			matching prefix and/or suffix.
			
			Matches are made case-insensitively.
			
			Acceptable patterns (using Python string.format-notation):
				={0}  : Match a whole word
				=={0} : Match entire field content
				*{0}* : Any substring
				{0}*  : Start of field (default)
				*{0}  : End of field
				>{0}  : Greater than
				>={0} : Greater than or equal
				<{0}  : Less than
				<={0} : Less than or equal
				^{0}  : Negate match
			These are native FileMaker comparison patterns/operators.
			However, the final "^" pattern is, seemingly, undocumented by
			FileMaker. This operator performs the inverse of "=", or can
			be combined with any of the other patterns to perform their
			inverse instead, eg.:
				^=={0} : Everything but exact string matches
				^*{0}* : Anything which doesn't contain the string
				etc.
			NB. More complex searches, which require a findquery, can not
			make use of the negation operator, as it doesn't work with
			compound queries. I guess that's why it's undocumented.
		"""
		kwargs = self._normalise_field_params(kwargs)
		
		if not kwargs:
			raise exceptions.FMNotSupportedError('Cannot perform find without parameters')
		
		if self.command not in ('find', 'findquery'):
			# First find of the day
			for key, val in kwargs.items():
				self._params[key] = val
				self._fields.append(key)
				
			self.command = 'find'
			
		else:
			if self.command == 'find':
				self._convert_to_findquery()
			
			# Append the new parameters to the findquery
			placeholders = self._add_query_fields(kwargs)
			compound = '({0})'.format(','.join(placeholders))
			self._params['-query'] = ';'.join((self._params['-query'], compound))
			
		return self
		
	def find_any(self, **kwargs):
		"""
			Add a logical-or search to the query.
			
			See the .find() method for argument documentation.
		"""
		if self.command not in ('find', 'findquery'):
			self.find(**kwargs)
			self._params['-lop'] = 'or'
			
		else:
			kwargs = self._normalise_field_params(kwargs)
			if self.command == 'find':
				self._convert_to_findquery()
			
			placeholders = self._add_query_fields(kwargs)
			compound = ';'.join('({0})'.format(q) for q in placeholders)
			self._params['-query'] = ';'.join((self._params['-query'], compound))
			
		return self
		
	def exclude(self, **kwargs):
		"""
			Exclude a subset from the current find.
			
			See the .find() method for argument documentation.
		"""
		self._convert_to_findquery()
		kwargs = self._normalise_field_params(kwargs)
		placeholders = self._add_query_fields(kwargs)
		compound = '!({0})'.format(','.join(placeholders))
		self._params['-query'] = ';'.join((self._params['-query'], compound))
		
		return self
		
	def exclude_any(self, **kwargs):
		"""
			Exclude any of several subsets from the current find.
			
			See the .find() method for argument documentation.
		"""
		self._convert_to_findquery()
		kwargs = self._normalise_field_params(kwargs)
		placeholders = self._add_query_fields(kwargs)
		compound = ';'.join('!({0})'.format(q) for q in placeholders)
		self._params['-query'] = ';'.join((self._params['-query'], compound))
		
		return self
		
	def filter(self, **kwargs):
		"""
			Apply find params to all current find params.
			
			See the .find() method for argument documentation.
			
			Performing a filter using a field already in use can result in
			unexpected behaviour by FileMaker, so attempting to do so will
			raise an FMNotSupportedError.
			
			Has no effect on any find()s (,etc.) performed afterward.
		"""
		self._convert_to_findquery()
		kwargs = self._normalise_field_params(kwargs)
		# Check for fields which already exist
		dupes = [key for key in kwargs if key in self._fields]
		if dupes:
			raise exceptions.FMNotSupportedError('Cannot filter on used fields; {0!r}'.format(dupes))
		placeholders = self._add_query_fields(kwargs)
		compound = ',{0})'.format(','.join(placeholders))
		self._params['-query'] = self._params['-query'].replace(')', compound)
		
		return self
		
	def reset_find(self):
		"""
			Clears any 'find' parameters, so to start afresh.
		"""
		self.command = self._DEFAULT_COMMAND
		self._reset_params()
		self._fields = []
		
		return self
		
	def sort(self, *args):
		"""
			Set the sort parameter/s of the results.
			
			Arguments can be either a string field-name, or a two-tuple of
			(field-name, order); where `order` indicates whether to sort
			ascending (the default) or descending.
			
			Acceptable values for the order are 'asc', 'desc', 'ascend',
			'descend', or the ASC and DESC constants; attributes of
			FMFindQuery instances.
		"""
		norm = {
				'asc': 'ascend',
				'desc': 'descend',
				}
		for idx, arg in enumerate(args):
			if isinstance(arg, basestring) or not hasattr(arg, '__iter__'):
				val = arg
				order = None
			else:
				val, order = arg
			
			self._params['-sortfield.{0}'.format(idx+1)] = val
			if order:
				order = norm.get(order, order)
				self._params['-sortorder.{0}'.format(idx+1)] = order
			
		return self
		
	def limit(self, max=None, skip=None):
		"""
			Set limits on the returned results to a subset of all matches.
			
			The `max` parameter indicates the maximum number of records
			to return.
			The `skip` parameter indicates how far through the set of all
			matches to begin returning records.
			
			Any arguments not supplied (or supplied as None) will be
			removed from the query parameters.
		"""
		if max is not None:
			self._params['-max'] = max
		elif '-max' in self._params:
			del(self._params['-max'])
		
		if skip is not None:
			self._params['-skip'] = skip
		elif '-skip' in self._params:
			del(self._params['-skip'])
		
		return self
		
	
class FMEditQuery(FMQuery):
	"""
		A special kind of Query for editing or creating records.
	"""
	def __init__(self, recid, db, layout, **kwargs):
		"""
			Initialise the Query for either an edit or new operation.
			
			If the given `recid` is None (must be specified explicitly),
			then the Query will be a "new" operation, otherwise it will
			be an "edit" of an existing record.
		"""
		# The db and layout params are required, but just passed through
		self._recid = recid
		command = 'new' if self._recid is None else 'edit'
		super(FMEditQuery, self).__init__(command=command, db=db, layout=layout, **kwargs)
		if self._recid is not None:
			self._params['-recid'] = self._recid
		
	def _reset_params(self, **kwargs):
		super(FMEditQuery, self)._reset_params(**kwargs)
		if self._recid is not None:
			self._params['-recid'] = self._recid
		
	
	def set(self, **kwargs):
		"""
			Add parameters to update on a record.
		"""
		params = self._normalise_field_params(kwargs)
		self._params.update(params)
		return self
		
	
class FMBinaryQuery(FMQuery):
	"""
		Used to request binaries from a server.
	"""
	grammar = 'cnt/data.{ext}'
	
	def __init__(self, id, field, type, repetition=None, **kwargs):
		"""
			In addition to normal FMQuery init args, requires:
				`id` of the record in question
				`field` name of the container
				`type` of the binary (ie. URL file extension)
			
			Additionally, a `repetition` number can be supplied, if you
			think you need that.
		"""
		self.grammar = self.grammar.format(ext=type)
		super(FMBinaryQuery, self).__init__(**kwargs)
		
		self._params['-recid'] = id
		self._params['-field'] = field
		if repetition is not None:
			self._params['-field'] += '({0})'.format(int(repetition))
		
	def __repr__(self):
		return '<{mod}.{cls} {id:x} {field}:{recid}>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__.__name__,
				id=id(self),
				field=self._params['-field'],
				recid=self._params['-recid'],
				)
	
