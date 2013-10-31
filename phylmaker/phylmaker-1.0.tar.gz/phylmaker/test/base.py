"""
	Unit-testing base class.
"""
import os
import unittest

import phylmaker.server
import phylmaker.result


class BaseTestCase(unittest.TestCase):
	"""
		Base class which test cases should inherit from.
		
		Covers things like preventing actual HTTP requests.
		
		NB! Remember to super() your setUp/tearDown/etc.!
	"""
	def setUp(self, **kwargs):
		super(BaseTestCase, self).setUp(**kwargs)
		self.server = TestServer()
		
	def tearDown(self, **kwargs):
		super(BaseTestCase, self).tearDown(**kwargs)
		
	
	def load_data(self, name):
		"""
			Load and return the `name`d data (as a file-like object).
		"""
		path = os.path.join(os.path.dirname(__file__), 'data', name)
		return open(path, 'r').read()
		
	

class TestServer(phylmaker.server.FMServer):
	"""
		Test server, which doesn't do any HTTP requesting.
		
		Should do as little as possible, and almost always defer to
		the super()class.
	"""
	response_data = None
	response_code = 200
	
	def __init__(self, netloc='example.com:8888', **kwargs):
		super(TestServer, self).__init__(netloc=netloc, **kwargs)
	
	def _request(self, *args, **kwargs):
		kwargs['_testing'] = True
		request = super(TestServer, self)._request(*args, **kwargs)
		# Add attributes so the request also looks a bit like a Response
		request.text = self.response_data
		request.status_code = int(self.response_code)
		return request
		
	def execute(self, *args, **kwargs):
		if self.response_data is None:
			raise ValueError('Test called execute() without response_data')
		return super(TestServer, self).execute(*args, **kwargs)
		
	
