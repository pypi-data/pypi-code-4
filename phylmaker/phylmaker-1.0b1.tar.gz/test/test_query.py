"""
	Testing Phylmaker query compiler.
"""
import urlparse

import phylmaker.exceptions
import phylmaker.query

from . import base


class QueryTests(base.BaseTestCase):
	"""
		Test query string manipulations
	"""
	def test_command(self):
		query = phylmaker.query.FMQuery(command='foo')
		assert str(query) in ['-foo', '-foo=']
		assert '-foo' in query.to_dict()
		assert not query.to_dict()['-foo']
		req = self.server._request(query)
		parts = urlparse.urlsplit(req.url)
		assert parts.query in ['-foo', '-foo=']
		
	def test_command_db(self):
		query = phylmaker.query.FMQuery(command='foo', db='bar')
		assert '-foo' in query.to_dict()
		assert query.to_dict()['-db'] == 'bar'
		req = self.server._request(query)
		parts = urlparse.urlsplit(req.url)
		params = urlparse.parse_qs(parts.query, keep_blank_values=True)
		assert params['-foo'] == ['']
		assert params['-db'] == ['bar']
		
	def test_db_instance(self):
		db = self.server.get_db('bar')
		query = phylmaker.query.FMQuery(command='foo', db=db)
		assert query.to_dict()['-db'] == 'bar'
		
	def test_layout(self):
		query = phylmaker.query.FMQuery(command='foo', layout='baz')
		assert query.to_dict()['-lay'] == 'baz'
		
	def test_layout_instance(self):
		layout = self.server.get_layout(db='bar', layout='baz')
		query = phylmaker.query.FMQuery(command='foo', layout=layout)
		params = query.to_dict()
		assert params['-lay'] == 'baz'
		assert params['-db'] == 'bar'
		
	def test_layout_db_conflict(self):
		# When a layout's db is different to the one specified, that's an error
		layout = self.server.get_layout(db='bar', layout='baz')
		self.assertRaises(
				phylmaker.exceptions.FMNotSupportedError,
				phylmaker.query.FMQuery,
				command='foo',
				db='pub',
				layout=layout,
				)
		
	def test_to_string(self):
		query = phylmaker.query.FMQuery(command='foo', db='bar/baz', layout=3)
		string = query.to_string()
		assert '-foo' in string
		assert '-db=bar%2Fbaz' in string
		assert '-lay=3' in string
		
	def test_execute(self):
		# Error without a server
		query = phylmaker.query.FMQuery(command='foo')
		self.assertRaises(phylmaker.exceptions.FMConnectionError, query.execute)
		# Works from a server.execute
		self.server.response_data = self.load_data('fmresultset_dbnames.xml')
		result = self.server.execute(query)
		# Works with passed-in server
		query = phylmaker.query.FMQuery(command='foo', server=self.server)
		result = query.execute()
		# Works getting query from server/layout
		layout = self.server.get_layout(db='foo', layout='bar')
		query = layout.get_query(command='baz')
		result = query.execute()
		
	def test_duplicate(self):
		query = phylmaker.query.FMQuery()
		query.duplicate(123)
		params = query.to_dict()
		assert '-dup' in params
		assert params['-recid'] == '123'
		
	def test_delete(self):
		query = phylmaker.query.FMQuery()
		query.delete(123)
		params = query.to_dict()
		assert '-delete' in params
		assert params['-recid'] == '123'
		
	

class FindQueryTests(base.BaseTestCase):
	def setUp(self, **kwargs):
		super(FindQueryTests, self).setUp(**kwargs)
		self.query = phylmaker.query.FMFindQuery(db='foo', layout='bar')
		
	def test_layout_source(self):
		# Make sure we can get one from the layout
		layout = self.server.get_layout(db='foo', layout='bar')
		query = layout.get_query('find')
		params = query.to_dict()
		assert '-find' in params
		# Quick-find interface
		query = layout.find(foo='bar')
		params = query.to_dict()
		assert '-find' in params
		assert params['foo'] == 'bar'
		# Blind quick-find
		query = layout.find()
		params = query.to_dict()
		assert '-findall' in params
		
	def test_get(self):
		self.query.get(123)
		params = self.query.to_dict()
		assert '-find' in params
		assert params['-recid'] == '123'
	def test_get_reset(self):
		# Doing a get should remove any previous find params
		self.query.find(foo='bar')
		self.query.get(123)
		params = self.query.to_dict()
		assert 'foo' not in params
		
	
	def test_findall(self):
		# With no filters, we're _supposed_ to use -findall (...right?)
		params = self.query.to_dict()
		assert '-findall' in params
		
	def test_single(self):
		self.query.find(foo='one')
		params = self.query.to_dict()
		assert '-find' in params
		assert params['foo'] == 'one'
		
	def test_multiple(self):
		self.query.find(foo='one', bar=2)
		params = self.query.to_dict()
		assert '-find' in params
		assert params['foo'] == 'one'
		assert params['bar'] == '2'
		assert params.get('-lop', 'and') == 'and'
		
	def test_invalid_fields(self):
		FMNSErr = phylmaker.exceptions.FMNotSupportedError
		self.assertRaises(FMNSErr, self.query.find, **{'-foo': 'bar'})
		self.assertRaises(FMNSErr, self.query.find, **{'foo.op': 'bar'})
		self.assertRaises(FMNSErr, self.query.find, **{'foo.global': 'bar'})
		self.assertRaises(FMNSErr, self.query.find, **{'foo.4': 'bar'})
		
	def test_any(self):
		# find_any() performs a logical OR
		# NB! This is NOT the same as the -findany command!
		self.query.find_any(foo='one', bar=2)
		params = self.query.to_dict()
		assert '-find' in params
		assert params['foo'] == 'one'
		assert params['bar'] == '2'
		assert params['-lop'] == 'or'
		
	def test_noop(self):
		# A find with no params is an error
		self.assertRaises(phylmaker.exceptions.FMNotSupportedError, self.query.find)
		
	def test_comp(self):
		# Different patterns for different folks
		self.query.find(foo='=bar')
		params = self.query.to_dict()
		assert '-find' in params
		assert params['foo'] == '=bar'
	def test_comp_multi(self):
		self.query.find(foo='bar*', bar='*baz')
		params = self.query.to_dict()
		assert params['foo'] == 'bar*'
		assert params['bar'] == '*baz'
	def test_comp_neq(self):
		# The logical NOT operator appears to be completely undocumented
		self.query.find(foo='^bar')
		params = self.query.to_dict()
		assert params['foo'] == '^bar'
	def test_comp_neq_convert(self):
		# However, the NOT operator does not work in findqueries :(
		self.query.find(foo='^bar')
		self.assertRaises(phylmaker.exceptions.FMNotSupportedError, self.query.find, bar='baz')
	def test_comp_neq_query(self):
		self.query.find(foo='bar')
		self.assertRaises(phylmaker.exceptions.FMNotSupportedError, self.query.find, bar='^baz')
		
	def test_reset(self):
		# Sometimes you just want to start over
		self.query.reset_find()
		params = self.query.to_dict()
		print params
		assert len(params) == 3
		assert '-findall' in params
		assert params['-db'] == 'foo'
		assert params['-lay'] == 'bar'
		# Now with something to actually reset
		self.query.find(foo='bar')
		self.query.limit(5, 10)
		self.query.sort('foo')
		params = self.query.to_dict()
		assert params['foo'] == 'bar'
		self.query.reset_find()
		params = self.query.to_dict()
		assert 'foo' not in params
		assert len(params) == 3
		
	def test_sort(self):
		self.query.sort('foo')
		params = self.query.to_dict()
		assert params['-sortfield.1'] == 'foo'
		assert params.get('-sortorder.1', 'ascend') == 'ascend'
		# Not resetting, to validate that we override previous sort
		self.query.sort(('foo', 'desc'))
		params = self.query.to_dict()
		assert params['-sortfield.1'] == 'foo'
		assert params['-sortorder.1'] == 'descend'
		assert '-sortfield.2' not in params
	def test_sort_order_const(self):
		self.query.sort(('foo', self.query.ASC))
		params = self.query.to_dict()
		assert params['-sortfield.1'] == 'foo'
		assert params['-sortorder.1'] == 'ascend'
		
	def test_sort_multi(self):
		self.query.sort('foo', 'bar')
		params = self.query.to_dict()
		assert params['-sortfield.1'] == 'foo'
		assert params['-sortfield.2'] == 'bar'
	def test_sort_multi_order(self):
		self.query.sort('foo', ('bar', 'desc'))
		params = self.query.to_dict()
		assert params['-sortfield.1'] == 'foo'
		assert params.get('-sortorder.1', 'ascend') == 'ascend'
		assert params['-sortfield.2'] == 'bar'
		assert params['-sortorder.2'] == 'descend'
		
	def test_limit_max(self):
		self.query.limit(max=10)
		params = self.query.to_dict()
		assert params['-max'] == '10'
	def test_limit_skip(self):
		self.query.limit(skip=10)
		params = self.query.to_dict()
		assert params['-skip'] == '10'
	def test_limit_both(self):
		self.query.limit(5, skip=10)
		params = self.query.to_dict()
		assert params['-skip'] == '10'
		assert params['-max'] == '5'
		
	def test_query_basic(self):
		# Test -findquery compound searches
		self.query.find(foo='one')
		self.query.find(bar='two', baz=3)
		params = self.query.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1);(q2,q3)'
		assert params['-q1'] == 'foo'
		assert params['-q1.value'] == 'one'
		assert params['-q2'] == 'bar'
		assert params['-q2.value'] == 'two'
		assert params['-q3'] == 'baz'
		assert params['-q3.value'] == '3'
		
	def test_query_any(self):
		# find_any() acts like repeated find()s
		self.query.find(foo='one')
		self.query.find_any(bar='two', baz=3)
		params = self.query.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1);(q2);(q3)'
		assert params['-q1'] == 'foo'
		assert params['-q1.value'] == 'one'
		assert params['-q2'] == 'bar'
		assert params['-q2.value'] == 'two'
		assert params['-q3'] == 'baz'
		assert params['-q3.value'] == '3'
		
	def test_exclude(self):
		# -findquery exclusions
		self.query.find(foo='one')
		self.query.exclude(bar='two', baz=3)
		params = self.query.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1);!(q2,q3)'
		assert params['-q1'] == 'foo'
		assert params['-q1.value'] == 'one'
		assert params['-q2'] == 'bar'
		assert params['-q2.value'] == 'two'
		assert params['-q3'] == 'baz'
		assert params['-q3.value'] == '3'
		
	def test_exclude_any(self):
		# exclude_any() acts like lots of exclude()s
		self.query.find(foo='one')
		self.query.exclude_any(bar='two', baz=3)
		params = self.query.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1);!(q2);!(q3)'
		assert params['-q1'] == 'foo'
		assert params['-q1.value'] == 'one'
		assert params['-q2'] == 'bar'
		assert params['-q2.value'] == 'two'
		assert params['-q3'] == 'baz'
		assert params['-q3.value'] == '3'
		
	def test_filter(self):
		self.query.find(foo='one')
		self.query.filter(bar='two')
		params = self.query.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1,q2)'
		assert params['-q1'] == 'foo'
		assert params['-q1.value'] == 'one'
		assert params['-q2'] == 'bar'
		assert params['-q2.value'] == 'two'
	def test_filter_each(self):
		self.query.find(foo='one')
		self.query.find(bar='two', baz=3)
		self.query.filter(fez='four')
		params = self.query.to_dict()
		assert params['-query'] == '(q1,q4);(q2,q3,q4)'
		assert params['-q4'] == 'fez'
		assert params['-q4.value'] == 'four'
	def test_filter_multi(self):
		self.query.find(foo='one')
		self.query.find(bar='two')
		self.query.filter(baz='three')
		self.query.filter(fez='four')
		params = self.query.to_dict()
		assert params['-query'] == '(q1,q3,q4);(q2,q3,q4)'
	def test_filter_before(self):
		self.query.find(foo='one')
		self.query.filter(bar='two')
		self.query.find(baz='three')
		params = self.query.to_dict()
		assert params['-query'] == '(q1,q2);(q3)'
	def test_filter_dupefield(self):
		# Unexpected things can happen when a filter overlaps a find
		# (because FM uses only the last query for each field in an AND)
		self.query.find(foo='one*')
		self.assertRaises(phylmaker.exceptions.FMNotSupportedError, self.query.filter, foo='*two')
		
	def test_returns(self):
		assert self.query.find_any(foo='one').find(bar='two')
		assert self.query.sort('foo')
		assert self.query.limit(10)
		assert self.query.filter(baz='three')
		assert self.query.exclude(fez='four')
		assert self.query.exclude_any(bez='five')
		
	def test_chaining(self):
		q = self.query.find(foo='one').exclude(bar='two').filter(baz='three').sort('foo').limit(10)
		assert q
		params = q.to_dict()
		assert '-findquery' in params
		assert params['-query'] == '(q1,q3);!(q2,q3)'
		assert params['-sortfield.1'] == 'foo'
		assert params['-max'] == '10'
		
	
class EditQueryTests(base.BaseTestCase):
	def setUp(self, **kwargs):
		super(EditQueryTests, self).setUp(**kwargs)
		self.recid = '123'
		self.query = phylmaker.query.FMEditQuery(recid=self.recid, db='foo', layout='bar')
		
	
	def test_base_new(self):
		query = phylmaker.query.FMEditQuery(recid=None, db='foo', layout='bar')
		assert query.command == 'new'
		params = query.to_dict()
		assert '-new' in params
		assert '-recid' not in params
		
	def test_base_edit(self):
		params = self.query.to_dict()
		assert '-edit' in params
		assert params['-recid'] == self.recid
		assert params['-db'] == 'foo'
		assert params['-lay'] == 'bar'
		
	def test_set(self):
		self.query.set(foo='bar')
		params = self.query.to_dict()
		assert params['foo'] == 'bar'
		
	def test_set_multiple(self):
		self.query.set(foo='bar', baz='fez')
		params = self.query.to_dict()
		assert params['foo'] == 'bar'
		assert params['baz'] == 'fez'
		
	def test_clear(self):
		self.query.set(foo=None, bar='')
		params = self.query.to_dict()
		assert params['foo'] == ''
		assert params['bar'] == ''
		
	
class BinaryQueryTests(base.BaseTestCase):
	"""
		Test queries for binaries
	"""
	def test_basic(self):
		query = phylmaker.query.FMBinaryQuery(
				db='foo', layout='bar',
				id=123, field='baz', type='png',
				)
		assert query
		assert query.grammar == 'cnt/data.png'
		params = query.to_dict()
		assert params['-recid'] == '123'
		assert params['-field'] == 'baz'
		
	def test_repetition(self):
		query = phylmaker.query.FMBinaryQuery(
				db='foo', layout='bar',
				id=123, field='baz', repetition=1, type='png',
				)
		params = query.to_dict()
		assert params['-field'] == 'baz(1)'
		
	
