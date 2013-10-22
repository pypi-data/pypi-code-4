# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_equals, assert_true, assert_false, assert_is, assert_is_instance

from datetime import date, time, datetime

from valhalla import Schema

test_data = {
	'valid_date': '12/06/1989',
	'valid_europe_date': '06/12/1898',
	'valid_europe_expanded': '06 Dec 1989',
	'invalid_date': '09/31/2013', # does not have 31 days
	'garbage_date': '19922-12 01',
	'valid_time': '12:06:24',
	'valid_24_time': '13:01:01',
	'invalid_12_time': '22:00:00',
	'invalid_24_time': '26:00:00',
	'garbage_time': '46:06- 24',
	'valid_datetime': '12/06/1989 12:06:24',
	'invalid_datetime': '09/31/2013 12:06:24',
	'my_birthday': '12/06/1989',
	'my_favorite_time': '04:20:00',
	'far_far_away': '2050-12-06',
	'long_time_ago': '1800-01-01'
}

def test_date():
	s = Schema()
	s.valid_date.date()
	s.valid_europe_date.date(format='europe')
	s.valid_europe_expanded.date(format='europe_expanded')
	s.invalid_date.date()
	s.garbage_date.date()

	s.validate(test_data)
	assert_false(s.valid)

	assert_true(s.valid_date.valid)
	assert_true(s.valid_europe_date.valid)
	assert_true(s.valid_europe_expanded.valid)
	assert_false(s.invalid_date.valid)
	assert_false(s.garbage_date.valid)

def test_time():
	s = Schema()
	s.valid_time.time()
	s.valid_24_time.time(format='military')
	s.invalid_12_time.time()
	s.invalid_24_time.time(format='military')
	s.garbage_time.time()

	s.validate(test_data)
	assert_false(s.valid)

	assert_true(s.valid_time.valid)
	assert_true(s.valid_24_time.valid)
	assert_false(s.invalid_12_time.valid)
	assert_false(s.invalid_24_time.valid)
	assert_false(s.garbage_time.valid)

def test_datetime():
	s = Schema()
	s.valid_datetime.datetime()
	s.invalid_datetime.datetime()

	s.validate(test_data)
	assert_false(s.valid)

	assert_true(s.valid_datetime.valid)
	assert_false(s.invalid_datetime.valid)

def test_time_before():
	s = Schema()
	s.my_birthday.date().time_before(date.today())
	s.far_far_away.date(format='american_scientific').time_before(date.today())
	s.long_time_ago.date(format='american_scientific').time_before(date.today())

	s.validate(test_data)
	assert_false(s.valid)

	assert_true(s.my_birthday.valid)
	assert_false(s.far_far_away.valid) # one day this assertion will be True :)
	assert_true(s.long_time_ago.valid)

def test_time_after():
	s = Schema()
	s.my_birthday.date().time_after(date.today())
	s.far_far_away.date(format='american_scientific').time_after(date.today())
	s.long_time_ago.date(format='american_scientific').time_after(date.today())

	s.validate(test_data)
	assert_false(s.valid)

	assert_false(s.my_birthday.valid)
	assert_true(s.far_far_away.valid)
	assert_false(s.long_time_ago.valid)

def test_time_between():
	s = Schema()
	s.my_birthday.date().time_between(date(1988, 1, 1), date.today())
	s.long_time_ago.date(format='american_scientific').time_between(date.today(), date(2055, 1, 1))

	s.validate(test_data)
	assert_false(s.valid)

	assert_true(s.my_birthday.valid)
	assert_false(s.long_time_ago.valid)