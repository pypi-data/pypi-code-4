"""
	Testing Phylmaker server interface.
"""
import urlparse
import base64

import phylmaker.exceptions
import phylmaker.server
import phylmaker.query

from . import base


class ServerTests(base.BaseTestCase):
	"""
		Test server operations.
		
		Does not actually perform requests, but uses FMServer._TESTING
		to acquire the Request objects themselves.
	"""
	def setUp(self, **kwargs):
		super(ServerTests, self).setUp(**kwargs)
		self.query = phylmaker.query.FMQuery(command='foo')
		
	
	def test_secure_schema(self):
		server = base.TestServer('example.com:123')
		request = server._request(self.query)
		assert request.url.startswith('http://')
		server = base.TestServer('example.com:123', secure=True)
		request = server._request(self.query)
		assert request.url.startswith('https://')
		
	def test_debug(self):
		# Just make sure it doesn't break completely
		server = base.TestServer('example.com:123', debug=True)
		server._request(self.query)
		
	def test_get_layout(self):
		# Make sure we can get FMLayouts via the FMServer
		layout = self.server.get_layout(db='foo', layout='bar')
		assert layout.db.id == 'foo'
		assert layout.id == 'bar'
		
	def test_list_layouts(self):
		# Fetch layouts using test data
		self.server.response_data = self.load_data('fmresultset_layoutnames.xml')
		res = self.server.get_layouts('db')
		assert len(res) == 3
		assert set(res) == set(['foo', 'bar', 'baz'])
		
	def test_auth_failure(self):
		# Make sure an auth failure gives a sensible exception
		self.server.response_data = self.load_data('forbidden.html')
		self.server.response_code = 401
		self.assertRaises(phylmaker.exceptions.FMConnectionError, self.server.get_layouts, 'db')
		
	def test_filemaker_error(self):
		# Make sure unexpected FileMaker error codes get raised
		self.server.response_data = self.load_data('fmresultset_error.xml')
		self.assertRaises(phylmaker.exceptions.FMDatabaseError, self.server.get_layouts, 'db')
		
	def test_no_results(self):
		# Make sure that "no records" isn't an error, in spite of having a code
		self.server.response_data = self.load_data('fmresultset_norecords.xml')
		self.server.get_layouts('db')
		
	
class DatabaseTests(base.BaseTestCase):
	"""
		Tests on the intermediary FMDatabase class
	"""
	def setUp(self, **kwargs):
		super(DatabaseTests, self).setUp(**kwargs)
		self.server.response_data = u''
		
	def get_request_auth(self, request):
		""" Return a 2-tuple of (user, pass) for the given request. """
		auth = request.headers['Authorization'].split(' ', 1)[1]
		return base64.b64decode(auth).split(':', 1)
		
	
	def test_auth(self):
		# Make sure auth details can be given direct to the FMDatabase
		db_auth = ['bar', 'baz']
		db = self.server.get_db(db='foo', user=db_auth[0], passphrase=db_auth[1])
		query = db.get_layout('spam').find(eggs='eggs')
		request = self.server._request(query)
		req_auth = self.get_request_auth(request)
		assert req_auth == db_auth
		
	def test_auth_server(self):
		# Make sure auth details can be inherited from the FMServer
		auth = [self.server.user, self.server._pass]
		db = self.server.get_db('foo')
		query = db.get_layout('spam').find(eggs='eggs')
		request = self.server._request(query)
		req_auth = self.get_request_auth(request)
		assert req_auth == auth
		
	
class LayoutTests(base.BaseTestCase):
	"""
		Tests on the FMLayout object
	"""
	def setUp(self, **kwargs):
		super(LayoutTests, self).setUp(**kwargs)
		self.layout = self.server.get_layout(db='foo', layout='bar')
		
	
	def test_instantiation(self):
		# Make sure the thing can be created on its own
		layout = phylmaker.server.FMLayout(
				server=self.server,
				db='foo',
				id='bar',
				)
		assert layout.db == 'foo'
		assert layout.id == 'bar'
		
	def test_repr(self):
		# Just testing that it doesn't error
		assert repr(self.layout)
		
	def test_fields(self):
		self.server.response_data = self.load_data('fmresultset_view.xml')
		fields = self.layout.get_fields()
		assert len(fields) == 2
		assert set(fields) == set(['text-field', 'number-field'])
		assert fields['text-field']['type'] == 'text'
		assert fields['number-field']['type'] == 'number'
		
	def test_get(self):
		self.server.response_data = self.load_data('fmresultset_record.xml')
		result = self.layout.get(1)
		assert result.id == 1
		assert result['text-field'] == 'one'
		assert result['number-field'] == 1
	def test_get_fail(self):
		self.server.response_data = self.load_data('fmresultset_notfound.xml')
		result = self.layout.get(123)
		assert result is None
		
	def test_new(self):
		self.server.response_data = self.load_data('fmresultset_record.xml')
		result = self.layout.new(foo='bar', baz='fez')
		assert result.id == 1
		
	def test_edit(self):
		self.server.response_data = self.load_data('fmresultset_record.xml')
		result = self.layout.edit(1, foo='bar')
		assert result.id == 1
		
	def test_duplicate(self):
		self.server.response_data = self.load_data('fmresultset_record.xml')
		result = self.layout.duplicate(1)
		assert result.id == 1
		
	def test_delete(self):
		self.server.response_data = self.load_data('fmresultset_deleted.xml')
		result = self.layout.delete(1)
		assert result is True
		
	
