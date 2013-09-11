# coding: utf-8

import json

__all__ = [
	"FormatDictProxy",
	"SerializeDictProxy",
	"PrefixDictProxy"
]

class FormatDictProxy(object):
	def __init__(self, backend, format=""):
		self.backend = backend
		self.format = str(format)

		for method in dir(backend):
			if method not in self.__dict__:
				self.__dict__[method] = getattr(backend, method)
	
	def __getitem__(self, key):
		return self.backend[self.format.format(str(key))]

	def __setitem__(self, key, value):
		self.backend[self.format.format(str(key))] = value
	
	def __delitem__(self, key):
		del self.backend[self.format.format(str(key))]
	
	def __contains__(self, key):
		return self.format.format(str(key)) in self.backend

class SerializeDictProxy(object):
	def __init__(self, backend, **kwargs):
		self.encoder = json.dumps
		self.decoder = json.loads
		self.backend = backend
		self.__dict__.update(kwargs)

		for method in dir(backend):
			if method not in self.__dict__:
				self.__dict__[method] = getattr(backend, method)

	def __getitem__(self, key):
		return self.decoder(self.backend[key])
	
	def __setitem__(self, key, value):
		self.backend[key] = self.encoder(value)

	def __contains__(self, key):
		return key in self.backend

class PrefixDictProxy(FormatDictProxy):
	def __init__(self, backend, prefix=""):
		FormatDictProxy.__init__(self, backend, str(prefix) + "{}")

