# coding: utf-8

import http.cookies

__all__ = [
	"SessionMiddleware",
	"Session"
]

class Session(object):
	def __init__(self, content=None, sid=None, persistent=None):
		self._data = {}

		self.persistent = True if persistent is True else False
		if sid is None:
			self.sid = self._generate_sid()
		else:
			self.sid = sid
		if content is not None:
			self._data.update(content)

	def __setitem__(self, key, value):
		self._data[key, value]
	
	def __getitem__(self, key):
		return self._data[key]

	def __delitem__(self, key):
		del self._data[key]

	def __contains__(self, key):
		return key in self._data

	def __len__(self):
		return len(self._data)

	def __iter__(self):
		return iter(self._data)

	def __nonzero__(self):
		return bool(self._data) or bool(self.persistent)

	def __repr__(self):
		if self.persistent:
			return "<session [persistent] {0} {1!r}>".format(
				self.sid, self._data)
		return "<session {0} {1!r}>".format(self.sid, self._data)

	def keys(self):
		return self._data.keys()

	def values(self):
		return self._data.values()

	def items(self):
		return self._data.items()

class SessionMiddleware(object):
	session_cookie = "SESSID"
	app = None
	persistence = None

	def __init__(self, app, persistence=None, session_cookie=None):
		if session_cookie is not None:
			self.session_cookie = session_cookie
		if persistence is not None:
			self.persistence = persistence
		else:
			self.persistence = {}
		self.app = app

	def __call__(self, environ, start_response):
		session = None

		reqcookie = http.cookies.SimpleCookie(environ.get("HTTP_COOKIE", ""))
		session_id = None
		if self.session_cookie in reqcookie:
			session_id = reqcookie[self.session_cookie].value
		del reqcookie

		if session_id and session_id in self.persistence:
			session = Session(self.persistence[session_id], session_id)
			session.persistent = True
		del session_id
		
		if session is None:
			session = Session()
		
		def _start_response(status, header):
			cookie = http.cookies.SimpleCookie()
			cookie[self.session_cookie] = session.sid
			header.append(tuple(str(cookie).split(": ", 1)))

			return start_response(status, header)

		environ["autism.session"] = session

		out = self.app(environ, _start_response)

		if session:
			self.persistence[session.sid] = session

		return out

