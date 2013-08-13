#!/usr/bin/env python
# coding=utf-8

from utils import count_if

# test for count_if
def test_count_if():
    assert count_if(lambda x: x > 0, [0, 1, 2, 3]) == 3
    assert count_if(lambda x: x == 0, [0, 1, 2, 3]) == 1
    assert count_if(lambda x: x < 0, [0, 1, 2, 3]) == 0


# test for count_if
def test_count_if_truth():
    assert count_if(lambda x: x, [0, 1, 2, 3]) == 3
    assert count_if(lambda x: x, [0, False, [], ()]) == 0
    assert count_if(lambda x: x, [0, 1, False, [], ()]) == 1


# test for count_if
def test_count_if_bad_usage():
    try:
        count_if(1, [0, 1, 2, 3])
        assert False, 'expect an Exception'
    except TypeError:
        assert True
    try:
        count_if(lambda x: x, 123)
        assert False, 'expect an Exception'
    except TypeError:
        assert True
