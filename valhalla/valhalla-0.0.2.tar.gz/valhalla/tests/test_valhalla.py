from nose.tools.trivial import assert_equals, assert_true, assert_false, assert_in

from .. import Schema, Field

def test_schema():
	s = Schema('Test Schema')
	assert_equals(s._fields, {})
	f = s.add_field('test_field', Field(s, 'test_field'))
	assert_equals(f, s.test_field)
	d = {'test_field': 'test_value'}
	s.validate(d)
	assert_true(s.valid)
	s.reset()
	assert_false(s.valid)

def test_field():
	s = Schema('Test Schema')
	s.second_field(alt='other_name', req=True)
	d = {
		'other_name': 'Test Value A',
		'second_field': 'Test Value B'
	}
	s.validate(d)
	assert_true(s.valid)
	assert_equals(s.other_name.result, 'Test Value A')
	assert_equals(s.second_field.result, 'Test Value A') # because this should not have been run twice
	s.reset()
	assert_false(s.valid)
	d = {'total_fail': 'will not work'}
	s.validate(d)
	assert_false(s.valid)
	assert_false(s.other_name.valid)
	assert_false(s.second_field.valid)
	assert_in('This field is required.', s.other_name.errors)

def test_filter():
	s = Schema('Test Schema')
	s.first_name.text()
	s.last_name.text(min_len=1, max_len=10)
	d = {
		'first_name': 'Jack',
		'last_name': 'Bauer'
	}
	s.validate(d)

	assert_equals(s.first_name.original, 'Jack')
	assert_equals(s.first_name.result, u'Jack')

	assert_true(s.last_name.valid)
	
	d = {
		'last_name': ''
	}
	s.reset()
	s.validate(d)
	assert_false(s.valid)