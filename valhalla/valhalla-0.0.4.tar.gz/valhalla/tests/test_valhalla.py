# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_equals, assert_true, assert_false, assert_in, assert_greater_equal

from valhalla import Schema, Field

test_schema_data = {
	'blank_field': '',
	'other_blank_field': '',
	'required_field': 'I am required',
	'match_me': 'match.com',
	'match_to_me': 'match.com',
	'not_a_good_match': 'notmatch.com'
}

test_data_two = {
	'password': '1234',
	'password_confirm': '12345',
	'field_one': 'i am required',
	'can_be_blank': ''
}

def test_schema():
	s = Schema()
	s.blank_field
	s.other_blank_field.blank(True)
	s.required_field.require()
	s.missing_field.require()
	s.match_me.match('match_to_me', 'not_a_good_match')
	s.match_to_me
	s.not_a_good_match

	s.validate(test_schema_data)
	assert_false(s.valid)

	assert_false(s.blank_field.valid)
	assert_true(s.other_blank_field.valid)
	assert_true(s.required_field.valid)
	assert_false(s.missing_field.valid)
	assert_false(s.match_me.valid)
	assert_false(s.match_to_me.valid)
	assert_false(s.not_a_good_match.valid)

	s = Schema(match=[('password', 'password_confirm')], require=['field_one', 'field_two'], blank=['can_be_blank'])
	s.password
	s.password_confirm
	s.field_one
	s.field_two
	s.can_be_blank

	s.validate(test_data_two)
	assert_false(s.valid)

	assert_false(s.password.valid)
	assert_false(s.password_confirm.valid)
	assert_true(s.field_one.valid)
	assert_false(s.field_two.valid)
	assert_true(s.can_be_blank.valid)

def test_field():
	s = Schema('Test Schema')
	s.second_field().alt('other_name').require()
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
	assert_in('This field cannot be missing.', s.other_name.errors)

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
	assert_false(s.valid),