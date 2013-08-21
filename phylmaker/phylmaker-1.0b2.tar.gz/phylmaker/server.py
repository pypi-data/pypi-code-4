"""
	FileMaker XML API server interface.
	
	Copyright (c) 2012, Mel Collins <mel@raumkraut.net>
	Released under the terms of the X11/MIT License
	(see included LICENSE file)
"""
import requests

from . import exceptions
from . import query
from . import result


class FMServer(object):
	"""
		A direct interface to a FM Server XML API.
	"""
	_URI = '{scheme}://{netloc}/fmi/xml/{grammar}'
	
	def __init__(self, netloc, user=None, passphrase=None, secure=False, debug=False, **kwargs):
		"""
			Create a new FMServer interface with the given params.
			
			`netloc` should consist of the host and port of the server to
			connect to. Any initial path segments (beyond those added by
			FileMaker itself) should also be included.
			`user` and `passphrase` contain the auth information to be
			included with every request.
			`secure` indicates whether to use https, or ordinary http, for
			the connection. It is advised to always use https, if your
			server setup supports it.
			`debug` indicates whether Phylmaker should output debug
			statements or not. Currently just writes to stdout.
		"""
		super(FMServer, self).__init__(**kwargs)
		self.secure = secure
		self.netloc = netloc.rstrip('/')
		self.user = user
		self._pass = passphrase
		self._debug = debug
		
		self.scheme = 'https' if self.secure else 'http'
		# Need a session to send requests
		self._http_session = requests.Session()
		example_uri = self._URI.format(scheme=self.scheme, netloc=self.netloc, grammar='')
		self._http_session.get_adapter(example_uri).max_retries = 2
		
	def __repr__(self):
		return '<{mod}.{cls} {netloc!r}>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__,
				netloc=self.netloc,
				)
	
	def _request(self, query, _testing=False):
		"""
			Perform an HTTP request for the given `query`.
			
			The (internal!) `_testing` parameter causes the method to
			not actually perform the request, and return the Request
			object, rather than a Response.
		"""
		uri = self._URI.format(
				scheme=self.scheme,
				netloc=self.netloc,
				grammar=query.grammar,
				)
		if query._db:
			auth = (query._db.user, query._db._pass)
		else:
			auth = (self.user, self._pass)
		req = requests.Request(
				method=query.method,
				url=uri,
				params=query.to_dict(),
				auth=auth,
				).prepare()
		
		if self._debug:
			print req.url
		if _testing:
			return req
			
		return self._http_session.send(req)
		
	def execute(self, query):
		"""
			Execute an FMQuery against the server.
		"""
		response = self._request(query)
		if not str(response.status_code).startswith('2'):
			raise exceptions.FMConnectionError('Request failed; received status {0} from server'.format(response.status_code))
		results = result.FMResultSet(data=response.text, server=self, db=query._db, layout=query._layout)
		# "No records found" is apparently an error worthy of a code (401)
		not_errors = (None, 0, 401)
		if results.error not in not_errors:
			raise exceptions.FMDatabaseError(results.error)
		return results
		
	
	def get_dbs(self):
		"""
			Return a dictionary of id:FMDatabase for the server.
		"""
		resultset = self.execute(query.FMQuery(command='dbnames'))
		return dict(
				(record['DATABASE_NAME'], FMDatabase(server=self, id=record['DATABASE_NAME']))
				for record in resultset
				)
		
	def get_db(self, db, user=None, passphrase=None):
		"""
			Return an instance of FMDatabase for the named database.
			
			Authentication information can optionally be supplied for
			this particular database instance. If not supplied, the auth
			details supplied to the parent FMServer will be used instead.
			
			Does not check that the specified database actually exists.
		"""
		return FMDatabase(server=self, id=db, user=user, passphrase=passphrase)
		
	def get_layouts(self, db):
		"""
			Return a dictionary of id:FMLayout for the given `db`.
			
			The `db` parameter can be either an FMDatabase instance, or
			the string ID thereof.
		"""
		if not hasattr(db, 'get_layouts'):
			db = self.get_db(db)
		return db.get_layouts()
		
	def get_layout(self, db, layout):
		"""
			Return a specific FMLayout for the given `db` and `layout`.
			
			The `db` parameter can be either an FMDatabase instance, or
			the string ID thereof.
			
			Does not check that the specified layout actually exists.
		"""
		if not hasattr(db, 'get_layout'):
			db = self.get_db(db)
		return db.get_layout(layout)
		
	

class FMDatabase(object):
	"""
		Provides an interface to a specific database.
		
		If a particular database requires different authentication
		credentials to those supplied to the parent FMServer, override
		values for `user` and `passphrase` can be specified during
		FMDatabase instatiation.
		
		Should need be instatiated only though an FMServer interface.
	"""
	def __init__(self, server, id, user=None, passphrase=None, **kwargs):
		super(FMDatabase, self).__init__(**kwargs)
		self._server = server
		self.id = id
		self.user = user if user is not None else server.user
		self._pass = passphrase  if passphrase is not None else server._pass
		
	def get_layouts(self):
		"""
			Return a dictionary of id:FMLayout for this database.
		"""
		resultset = self._server.execute(query.FMQuery(command='layoutnames', db=self))
		layouts = [record['LAYOUT_NAME'] for record in resultset]
		return dict(
				(name, FMLayout(server=self._server, db=self, id=name))
				for name in layouts
				)
		
	def get_layout(self, layout):
		"""
			Return a specific layout from this database.
			
			Does not check that the specified layout actually exists.
		"""
		return FMLayout(server=self._server, db=self, id=layout)
		
	
class FMLayout(object):
	"""
		Provides an interface to a specific layout.
		
		Should need be instantiated only via an FMServer or FMDatabase.
	"""
	def __init__(self, server, db, id, **kwargs):
		super(FMLayout, self).__init__(**kwargs)
		self._server = server
		self.db = db
		self.id = id
		
	def __repr__(self):
		return '<{mod}.{cls} {db}/{id} ({netloc})>'.format(
				mod=self.__class__.__module__,
				cls=self.__class__.__name__,
				netloc=self._server.netloc,
				db=self.db.id,
				id=self.id,
				)
	
	def get_query(self, command):
		"""
			Provides an FMQuery, on this layout, for the given `command`.
		"""
		return query.FMQuery(server=self._server, command=command, db=self.db, layout=self.id)
		
	def get_fields(self):
		"""
			Provides a dictionary of field information for this layout.
		"""
		q = self.get_query('view')
		return self._server.execute(q).fields
		
	
	def get(self, recid):
		"""
			Fetch the record with the given `recid`.
			
			Returns None if no such record exists.
		"""
		q = query.FMFindQuery(server=self._server, db=self.db, layout=self.id)
		try:
			results = q.get(recid).execute()
		except exceptions.FMDatabaseError, err:
			if err.code == 101:
				return None
			raise
		return results[0]
		
	def find(self, **kwargs):
		"""
			Quick interface to perform a find operation on this layout.
			
			Returns a Query instance, which can be further refined
			and/or executed.
		"""
		q = query.FMFindQuery(server=self._server, db=self.db, layout=self.id)
		if kwargs:
			q.find(**kwargs)
		return q
		
	def new(self, **kwargs):
		"""
			Create a new record on the layout, with the given `kwargs`.
			
			Returns the new FMRecord instance.
		"""
		q = query.FMEditQuery(recid=None, server=self._server, db=self.db, layout=self.id)
		results = q.set(**kwargs).execute()
		return results[0]
		
	def edit(self, record, **kwargs):
		"""
			Edit the given `record`, setting the given `kwargs`.
			
			The supplied `record` should be either an FMRecord instance,
			or a specific FileMaker `recid`.
			
			Returns the FMRecord instance of the edited record.
		"""
		# Check ancestry in case it's some random object with an .id
		if isinstance(record, result.FMRecord):
			record = record.id
		q = query.FMEditQuery(recid=record, server=self._server, db=self.db, layout=self.id)
		
		results = q.set(**kwargs).execute()
		return results[0]
		
	def duplicate(self, record):
		"""
			Duplicate the given `record`.
			
			The supplied parameter should be either an FMRecord instance,
			or a specific FileMaker `recid`.
			
			Returns the FMRecord instance of the created duplicate.
		"""
		# Lots of things have an `id`, so we check ancestry
		if isinstance(record, result.FMRecord):
			record = record.id
		q = query.FMQuery(server=self._server, db=self.db, layout=self.id)
		
		results = q.duplicate(record).execute()
		return results[0]
		
	def delete(self, record):
		"""
			Delete the given `record`.
			
			The supplied parameter should be either an FMRecord instance,
			or a specific FileMaker `recid`.
			
			Returns True if the record was deleted, or False if there was
			no record there in the first place. Either way, there should
			be no record with that `recid` afterward.
		"""
		# We use isinstance because lots of things have an `id`
		if isinstance(record, result.FMRecord):
			record = record.id
		q = query.FMQuery(server=self._server, db=self.db, layout=self.id)
		try:
			results = q.delete(record).execute()
		except exceptions.FMDatabaseError, err:
			if err.code == 101:
				return False
			raise
		return True
		
	
