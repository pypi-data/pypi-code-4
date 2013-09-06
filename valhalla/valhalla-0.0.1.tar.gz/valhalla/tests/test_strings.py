from nose.tools.trivial import assert_equals, assert_true, assert_false

from .. import Schema

def _blank_schema():
	return Schema('Sample Schema')

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
		'flanking_spaces': '        everybody do the dinosaur      ',
		'upper_case': 'I AM THE RAWRMACHINE',
		'lower_case': 'i am the quiet mouse'
	}

def test_text():
	s = _blank_schema()
	s.random_string.text()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()
	s.actual_numbers.text()

	s.validate(_sample_data())
	assert_false(s.valid)

def test_alnum():
	s = _blank_schema()
	s.alnum_string.alnum()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()
	s.alpha_string.alnum()
	s.actual_numbers.alnum()

	s.validate(_sample_data())

	assert_false(s.valid)
	assert_false(s.actual_numbers.valid)
	assert_true(s.alpha_string.valid)

def test_alpha():
	s = _blank_schema()
	s.alpha_string.alpha()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()
	s.actual_numbers.alpha()
	s.alnum_string.alpha()

	assert_false(s.valid)
	assert_false(s.actual_numbers.valid)
	assert_false(s.alnum_string.valid)

def test_numeric():
	s = _blank_schema()
	s.numeric_string.numeric()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()

	s.actual_numbers.numeric()
	s.validate(_sample_data())

	assert_false(s.valid)

def test_nonblank():
	s = _blank_schema()
	s.random_string.nonblank()
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()
	s.blank_string.nonblank()
	s.validate(_sample_data())

	assert_false(s.valid)

def test_removespaces():
	s = _blank_schema()
	s.awkward_spaces.removespaces()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.awkward_spaces.result, 'openthedoorgetonthefloorrr')

def test_strip():
	s = _blank_schema()
	s.flanking_spaces.strip()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.flanking_spaces.result, 'everybody do the dinosaur')

def test_lower():
	s = _blank_schema()
	s.upper_case.lower()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.upper_case.result, 'i am the rawrmachine')

def test_upper():
	s = _blank_schema()
	s.lower_case.upper()
	s.validate(_sample_data())

	assert_true(s.valid)
	assert_equals(s.lower_case.result, 'I AM THE QUIET MOUSE')

def test_regex():
	s = _blank_schema()
	s.numeric_string.regex(r'\d')
	s.validate(_sample_data())

	assert_true(s.valid)

	s = _blank_schema()
	s.alpha_string.regex(r'\d')
	s.validate(_sample_data())

	assert_false(s.valid)