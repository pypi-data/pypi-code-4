from nose.tools.trivial import (assert_equals, assert_true)

from valhalla import Schema

test_data = {
    'some_dict': {'one': 'fish', 'two': 'fish', 'red': 'fish', 'blue': 'fish'},
    'some_list': ['alpha', 'bravo', 'charlie', 'delta'],
    'some_other_list': ['alpha', 'bravo', 'charlie']
}


def test_drop_keys():
    s = Schema()
    s.some_dict.drop_keys('one', 'two')

    s.validate(test_data)
    assert_true(s.valid)

    assert_equals(s.some_dict.result, {'red': 'fish', 'blue': 'fish'})


def test_contains():
    s = Schema()
    s.some_list.contains('bravo')
    s.some_other_list.contains('alpha', 'bravo')

    s.validate(test_data)
    assert_true(s.valid)
