# coding=utf-8
from mock import Mock
from any_valid import AnyValid, Int, OneOf


def check_valid_1_param(valid_input, value, expected_success):
    m = Mock()
    m(value)
    try:
        m.assert_called_once_with(valid_input)
    except AssertionError:
        if expected_success:
            raise


def test_int():
    for kw_args, sub_tests in [
        ({},
         [(-3, True), (0, True), (123, True), (None, False), ('2', True)]),
        ({'min': 3},
         [(-3, False), (0, False), (123, True), (None, False), ('2', False)]),
        ({'min': -3, 'max': 5},
         [(-3, True), (0, True), (123, False), (None, False), ('2', True)]),
    ]:
        valid_input = AnyValid(Int(**kw_args))
        for value, expected_success in sub_tests:
            yield check_valid_1_param, valid_input, value, expected_success

def test_one_of():
    for items, sub_tests in [
        (['http', 'https'],
         [('ftp', False), ('http', True), ('https', True), ('file', False)]),
        (xrange(3),
         [(0, True), (1, True), (2, True), (3, False), ('2', False)]),
    ]:
        valid_input = AnyValid(OneOf(items))
        for value, expected_success in sub_tests:
            yield check_valid_1_param, valid_input, value, expected_success
