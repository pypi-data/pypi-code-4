# -*- coding: utf-8 -*-
import re,sys

if sys.version_info[0]==2:
	from urllib2 import unquote
elif sys.version_info[0]>=3:
	from urllib.parse import unquote

class HTTPRequestData(object):
	def __init__(self,post_values,query_string,cookies):
		self.post_values = unquote(post_values.replace('+',' '))
		self.query_string = unquote(query_string.replace('+',' '))
		self.cookies = unquote(cookies.replace('+',' '))
		
	# Probe function
	@staticmethod
	def _probe_value(data,varname,encoding='utf-8'):
		rx = re.compile('%s=([^&]+)' % varname)
		miter = rx.finditer(data)
		try:
			match = miter.next()
			return unicode(match.groups()[0],encoding)
		except StopIteration:
			return None
	
	def get_post_value(self,varname):
		return HTTPRequestData._probe_value(self.post_values,varname)
	
	def get_qs_value(self,varname):
		return HTTPRequestData._probe_value(self.query_string,varname)
	
	def get_cookie_value(self,varname):
		return HTTPRequestData._probe_value(self.cookies,varname)

	def get_any_value(self,varname):
		val = self.get_post_value(varname)
		if not val:
			val = self.get_qs_value(varname)
		if not val:
			val = self.get_cookie_value(varname)
		return val
