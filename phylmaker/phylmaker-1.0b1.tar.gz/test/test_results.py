"""
	Testing phylmaker results parser.
"""
import phylmaker.result

from . import base


class FmResultSetTests(base.BaseTestCase):
	"""
		Test processing the "fmresultset" grammar.
	"""
	grammar = phylmaker.result.FMResultSetGrammar
	
	def test_dbnames(self):
		data = self.load_data('fmresultset_dbnames.xml')
		res = phylmaker.result.FMResultSet(data=data, grammar=self.grammar)
		# Check the fields
		assert len(res.fields) == 1
		assert 'DATABASE_NAME' in res.fields
		# Check the data
		assert res.database == 'DBNAMES'
		assert res.layout == ''
		assert res.count == len(list(res))
		assert res.total == res.count
		assert res.error == 0
		for record in res:
			assert len(record) == len(res.fields)
			# Records for dbnames queryies have no IDs
			assert record.id == 0
			assert record._mod_id == 0
		
	def test_layout(self):
		data = self.load_data('fmresultset_record.xml')
		res = phylmaker.result.FMResultSet(data=data, grammar=self.grammar)
		# Check 'em
		assert res.database == 'FOO'
		assert res.layout == 'bar'
		
	def test_indexing(self):
		data = self.load_data('fmresultset_dbnames.xml')
		res = phylmaker.result.FMResultSet(data=data, grammar=self.grammar)
		count = res.count
		for idx in range(count):
			assert res[idx]
		self.assertRaises(IndexError, res.__getitem__, count)
		self.assertRaises(TypeError, res.__getitem__, 'foo')
		
	def test_unicode(self):
		data = self.load_data('fmresultset_dbnames.xml').replace('<data>one</data>', u'<data>\xf8ne</data>')
		res = phylmaker.result.FMResultSet(data=data, grammar=self.grammar)
		assert res[0]['DATABASE_NAME'] == u'\xf8ne'
		
	

class FmRecordTests(base.BaseTestCase):
	"""
		Test handling FMRecord objects.
	"""
	grammar = phylmaker.result.FMResultSetGrammar
	
	def setUp(self, **kwargs):
		super(FmRecordTests, self).setUp(**kwargs)
		self.server.response_data = self.load_data('fmresultset_records.xml')
		self.layout = self.server.get_layout('foo', 'bar')
		self.res = self.layout.find().execute()
		self.records = dict((rec.id, rec) for rec in self.res)
		
	
	def check_text_field(self, id, check):
		val = self.records[id]['text-field']
		assert val == check
		assert isinstance(val, check.__class__)
	def test_text_fields(self):
		self.check_text_field(1, u'one')
		self.check_text_field(2, u'')
		self.check_text_field(3, u'')
		self.check_text_field(4, u'm\xf8\xf8se')
		self.check_text_field(5, u'null')
		
	def test_number_fields(self):
		assert self.records[1]['number-field'] == 1
		assert self.records[2]['number-field'] == 2
		assert self.records[3]['number-field'] is None
		assert self.records[4]['number-field'] == 0
		assert self.records[5]['number-field'] is None
		
	
	def test_edit(self):
		record = self.records[1]
		mod_id = record._mod_id
		record['text-field'] = 'edited'
		record['number-field'] = 123
		self.server.response_data = self.load_data('fmresultset_record.xml')
		saved = record.save()
		assert saved
		
	def test_edit_noop(self):
		record = self.records[1]
		mod_id = record._mod_id
		saved = record.save()
		assert not saved
		assert record._mod_id == mod_id
		
	def test_nonedit_noop(self):
		record = self.records[1]
		mod_id = record._mod_id
		record['text-field'] = str(record['text-field'])
		saved = record.save()
		assert not saved
		assert record._mod_id == mod_id
		
	
	def test_delete(self):
		self.server.response_data = self.load_data('fmresultset_deleted.xml')
		result = self.records[1].delete()
		assert result is True
		
	
class FmContainerTests(base.BaseTestCase):
	"""
		Test records with binaries (containers).
	"""
	grammar = phylmaker.result.FMResultSetGrammar
	
	def setUp(self, **kwargs):
		super(FmContainerTests, self).setUp(**kwargs)
		self.data = self.load_data('fmresultset_record_binary.xml')
		self.res = phylmaker.result.FMResultSet(data=self.data, grammar=self.grammar, server=self.server)
		self.record = self.res[0]
		
	
	def test_url(self):
		container = self.record['binary-field']
		assert hasattr(container.__class__, 'read')
		params = container._query.to_dict()
		assert params['-db'] == self.res.database
		assert params['-lay'] == self.res.layout
		assert params['-recid'] == '1'
		assert params['-field'] == 'binary-field(1)'
		
	
