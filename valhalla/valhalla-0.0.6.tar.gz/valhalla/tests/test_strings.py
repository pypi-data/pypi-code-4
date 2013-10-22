# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_equals, assert_true, assert_false

from valhalla import Schema

def _sample_data():
	return {
		'blank_string': '',
		'none_type': None,
		'alpha_string': 'abcdefgh',
		'alnum_string': 'abc123',
		'numeric_string': '123456',
		'random_string': '1232 fsdfdsfs 993132.....fdsfd#@#@KLJFD(((#@)_',
		'actual_numbers': 1234566779999,
		'awkward_spaces': 'open   the    door get on the    floo   rrr',
		'flanking_spaces': '        everybody walk the dinosaur      ',
		'upper_case': 'I AM THE RAWRMACHINE',
		'lower_case': 'i am the quiet mouse',
		'noncanonical_string': 'THERE IS NOTHING-CANONICAL__ABOUTMEEEEEE333            see?',
		'notslugified': 'I AM NOT SLUGIFIED #@(#*@(#@ OMG PUNCTU3232...ATION    ---- who submits data like this anyway?'
	}

def test_text():
	s = Schema()
	s.random_string.text()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()
	s.actual_numbers.text()

	s.validate(_sample_data())
	assert_false(s.valid)

def test_alnum():
	s = Schema()
	s.alnum_string.alnum()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()
	s.alpha_string.alnum()
	s.actual_numbers.alnum()

	s.validate(_sample_data())

	assert_false(s.valid)
	assert_false(s.actual_numbers.valid)
	assert_true(s.alpha_string.valid)

def test_alpha():
	s = Schema()
	s.alpha_string.alpha()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()
	s.actual_numbers.alpha()
	s.alnum_string.alpha()

	assert_false(s.valid)
	assert_false(s.actual_numbers.valid)
	assert_false(s.alnum_string.valid)

def test_numeric_string():
	s = Schema()
	s.numeric_string.numeric_string()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()

	s.actual_numbers.numeric_string()
	s.validate(_sample_data())

	assert_false(s.valid)

def test_nonblank():
	s = Schema()
	s.random_string.nonblank()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()
	s.blank_string.nonblank()
	s.validate(_sample_data())

	assert_false(s.valid)

def test_removespaces():
	s = Schema()
	s.awkward_spaces.removespaces()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.awkward_spaces.result, 'openthedoorgetonthefloorrr')

def test_strip():
	s = Schema()
	s.flanking_spaces.strip()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.flanking_spaces.result, 'everybody walk the dinosaur')

def test_lower():
	s = Schema()
	s.upper_case.lower()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.upper_case.result, 'i am the rawrmachine')

def test_upper():
	s = Schema()
	s.lower_case.upper()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.lower_case.result, 'I AM THE QUIET MOUSE')

def test_regex():
	s = Schema()
	s.numeric_string.regex(r'\d')
	s.validate(_sample_data())

	assert_true(s.valid)

	s = Schema()
	s.alpha_string.regex(r'\d')
	s.validate(_sample_data())

	assert_false(s.valid)

def test_canonize():
	s = Schema()
	s.noncanonical_string.canonize()

	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.noncanonical_string.result, u'there_is_nothing_canonical_aboutmeeeeee333_see?')

def test_slugify():
	s = Schema()
	s.notslugified.slugify()

	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.notslugified.result, u'i-am-not-slugified--omg-punctu3232ation---------who-submits-data-like-this-anyway')