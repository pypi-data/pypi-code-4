"""
WSMan Commmand Filter Module

@copyright: 2010-2012
@author: Joseph Tallieu <joseph_tallieu@dell.com>
@organization: Dell Inc. - PG Validation
@license: GNU LGLP v2.1
"""
#    This file is part of WSManAPI.
#
#    WSManAPI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 2.1 of the License, or
#    (at your option) any later version.
#
#    WSManAPI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with WSManAPI.  If not, see <http://www.gnu.org/licenses/>.


from wsman.provider.winrm import WinRM
from wsman.provider.wsmancli import WSManCLI

class Filter(object):

	def __init__(self, dialect="", query=""):
		self._dialect = dialect
		self._query = query


	def get_dialect(self):
		return self._dialect

	def get_query(self):
		return self._query

	def _set_query(self, value):
		self._query = value

	def _set_dialect(self, value):
		self._dialect = value

	def __call__(self, provider, opts={}):
		return {"query": self._query, "dialect": self._dialect}

	dialect = property(get_dialect, _set_dialect)
	query = property(get_query, _set_query)


 

class SelectorFilter(Filter):
	def __init__(self, query=""):
		super(SelectorFilter, self).__init__("http://schemas.dmtf.org/wbem/wsman/1/wsman/SelectorFilter", query)


class XPathFilter(Filter):
	def __init__(self, query=""):
		super(XPathFilter, self).__init__("http://www.w3.org/TR/1999/REC-xpath-19991116", query)


class CQLFilter(Filter):
	def __init__(self, query=""):
		super(CQLFilter, self).__init__("http://schemas.dmtf.org/wbem/cql/1/dsp0202.pdf", query)


class WQLFilter(Filter):
	def __init__(self, query=""):
		super(WQLFilter, self).__init__("http://schemas.microsoft.com/wbem/wsman/1/WQL", query)

	"""
	def __call__(self, provider, opts={}):
		print "Provider class ", provider.__class__.__name__
		print isinstance(provider, WSManCLI)
		args = super(WQLFilter, self).__call__(provider, opts)
		args["cim_class"]  = "*"
		return args
	"""