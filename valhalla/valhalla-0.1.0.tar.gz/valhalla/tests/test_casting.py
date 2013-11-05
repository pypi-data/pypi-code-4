# -*- coding: utf-8 -*-

from nose.tools.trivial import (
    assert_equals, assert_true, assert_false,
    assert_is_instance
)

from valhalla import Schema

test_data = {
    'true_value': 'i am truth',
    'false_value': '',
    'str_false_1': 'false',
    'str_false_2': 'undefined',
    'str_false_3': '0',
    'str_false_4': '[]',
    'str_false_5': '{}',
    'str_false_6': 'None',
    'integer_value': '54',
    'float_value': '4.23',
    'not_integer': 'monkey time',
    'sizable_number': '12390858430439843049084325754382940234',
    'decimal_value': '4.5',
    'not_decimal_value': '4',
    'string_value': 'i am a string'
}


def test_boolean():
    s = Schema(blank='all')
    s.true_value.boolean()
    s.false_value.boolean()
    s.validate(test_data)
    assert_true(s.valid)
    assert_true(s.true_value.result)
    assert_equals(s.false_value.result, False)


def test_strbool():
    s = Schema(blank='all', strip_blank=False)
    s.true_value.strbool()
    s.str_false_1.strbool()
    s.str_false_2.strbool()
    s.str_false_3.strbool()
    s.str_false_4.strbool()
    s.str_false_5.strbool()
    s.str_false_6.strbool()

    s.validate(test_data)
    assert_true(s.valid)

    assert_true(s.true_value.result)
    assert_equals(s.str_false_1.result, False)
    assert_equals(s.str_false_2.result, False)
    assert_equals(s.str_false_3.result, False)
    assert_equals(s.str_false_4.result, False)
    assert_equals(s.str_false_5.result, False)
    assert_equals(s.str_false_6.result, False)


def test_integer():
    s = Schema()
    s.integer_value.integer()
    s.float_value.integer()
    s.not_integer.integer()

    s.validate(test_data)
    assert_false(s.valid)

    assert_true(s.integer_value.valid)
    assert_false(s.float_value.valid)
    assert_false(s.not_integer.valid)

    assert_is_instance(s.integer_value.result, int)


def test_longint():
    s = Schema()
    s.integer_value.longint()
    s.float_value.longint()
    s.sizable_number.longint()

    s.validate(test_data)
    assert_false(s.valid)

    assert_is_instance(s.integer_value.result, long)
    assert_is_instance(s.sizable_number.result, long)


def test_numeric():
    s = Schema()
    s.integer_value.numeric()
    s.float_value.numeric()

    s.validate(test_data)
    assert_true(s.valid)

    assert_is_instance(s.integer_value.result, int)
    assert_is_instance(s.float_value.result, float)


def test_decimal():
    s = Schema()
    s.decimal_value.decimal()
    s.not_decimal_value.decimal()
    s.string_value.decimal()

    s.validate(test_data)
    assert_false(s.valid)

    assert_true(s.decimal_value.valid)
    assert_true(s.not_decimal_value.valid)
    assert_false(s.string_value.valid)


def test_string():
    pass


def test_none():
    pass
