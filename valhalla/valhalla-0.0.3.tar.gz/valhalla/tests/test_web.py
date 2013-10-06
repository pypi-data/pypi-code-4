from nose.tools.trivial import assert_equals, assert_true, assert_false

from .. import Schema

def _blank_schema():
	return Schema('Test Schema')

def _sample_data():
	return {
		'valid_email': 'petermelias@gmail.com',
		'invalid_email': 'fdsfdsf3343232@dsfdsfds',
		'invalid_email2': 123445455444,
		'invalid_email3': '1111111111111111111',
		'valid_ipv4': '127.0.0.1',
		'invalid_ipv4': '12333330',
		'invalid_ipv42': '1233.122.22.22'
	}

def test_email():
	s = _blank_schema()
	s.valid_email.email()
	s.invalid_email.email()
	s.invalid_email2.email()
	s.invalid_email3.email()
	s.validate(_sample_data())

	assert_true(s.valid_email.valid)
	assert_false(s.invalid_email.valid)
	assert_false(s.invalid_email2.valid)
	assert_false(s.invalid_email3.valid)

def test_ipv4():
	s = _blank_schema()
	s.valid_ipv4.ipv4()
	s.invalid_ipv4.ipv4()
	s.invalid_ipv42.ipv4()

	s.validate(_sample_data())

	assert_true(s.valid_ipv4.valid)
	assert_false(s.invalid_ipv4.valid)
	assert_false(s.invalid_ipv42.valid)