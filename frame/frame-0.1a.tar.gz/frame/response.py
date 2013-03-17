from dotdict import DotDict
from errors import HTTPError, Error404
import datetime
from _routes import routes
from _config import config
import os
from util import format_date, get_gmt_now


class Response(object):
	'''
	The :class:`Response` class stores a collection of data about the HTTP response. It is
	used by the :class:`frame._app.App` to deliver information to the client. The current
	:class:`Response` object provides interfaces to:
	
	* Cookie creation and deletion
	* Set response status line and headers
	* Append keyword arguments to the controller action method that is called
	
	'''
	
	def __init__(self, app, action, params={}):
		if not action:
			raise Error404

		#: The Frame application
		self.app = app
		self.action = action
		self.params = params
		self._body = None
		
		# For consistency, attach self to app
		if app:
			app.response = self
		
		# Attempt to set the action controller's 'response' attribute
		if hasattr(action, 'im_self'):
			action.im_self.response = self
		
		#: A :mod:`frame.dotdict.DotDict` that stores the response headers
		self.headers = DotDict(config.response.default_headers)
		self.headers.update({
			'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0',
			'Pragma': 'no-cache'
		})
		self.status = '200 OK'
		
		#: Additional keyword arguments to pass off to the controller action method
		#: when it is called
		self.additional_params = {}
		
	@classmethod
	def from_data(cls, status, headers, body):
		response = cls(None, 'placeholder')
		response.status = status
		response.headers = DotDict(headers)
		response.body = body
		return response
			
	def set_cookie(self, key, value, expires=1, domain=None, path='/', secure=False, http_only=False):
		'''
		Send a cookie to the client.
		
		:param key: Key to use for cookie
		:param value: Data to pass to cookie
		:param expires: How long (in hours) until the cookie expires
		:param domain: Domain that the cookie should apply to
		:param path: Path that the cookie should apply to
		:param secure: Whether or not "Secure" flag should be passed to cookie
		:param http_only: Whether or not "HttpOnly" flag should be passed to cookie
		'''
		
		cookie = ["%s=%s" % (key, value)]

		if expires:
			now = get_gmt_now()
			then = now + datetime.timedelta(hours=expires)
			cookie.append("Expires=%s" % format_date(then))
		if domain:
			cookie.append("Domain=%s" % domain)
		if path:
			cookie.append("Path=%s" % path)
		if secure:
			cookie.append("Secure")
		if http_only:
			cookie.append("HttpOnly")

		self.headers['Set-Cookie'] = '; '.join(cookie)

	def delete_cookie(self, key):
		'''
		A helper function to expire a cookie and change its value to 'deleted' (just in case
		for some reason it isn't expired).
		
		:param key: The key of the cookie to expire
		'''
		self.headers['Set-Cookie'] = "%s=deleted; Expires=Thu, Jan 01 1970 00:00:00 GMT" % key

	def start_response(self):
		'''
		Starts the WSGI response back to the server. Sends the status line and a list of
		header tuples.
		
		.. deprecated:: 0.1
		   Handled by Frame application instead.
		'''
		self._start_response(self.status, self.headers.items())

	def render(self):
		'''
		Calls the controller action with the parameters passed via the params
		dictionary and additional_params dictionary. Saves output to :attr:`_body`.
		'''
		
		# Must render the page before we send start_response; otherwise, controller-set
		# headers will not get set in time.
		result = self.action(**dict(
			self.params.items() +
			self.additional_params.items()))
		
		if result is None or isinstance(result, dict):
			method_name = self.action.__name__
			
			if hasattr(self.action.im_self, '__resource__'):
				template_dir = self.action.im_self.__resource__['template_dir']
				template_path = os.path.join(template_dir, method_name + '.html')
			
				result = self.action.im_self.get_template(template_path).render(
					result if result else {})
					
			else:
				template_dir = self.action.im_self.__class__.__name__.lower()
				template_path = os.path.join(template_dir, method_name + '.html')
				
				result = self.action.im_self.get_template(template_path).render(
					result if result else {})

		self._body = result

	@property
	def body(self):
		if self._body is None:
			self.render()
		return self._body
		
	@body.setter
	def body(self, value):
		self._body = value
		
		
# Horrible hack to solve circular dependency problem
HTTPError.response_class = Response