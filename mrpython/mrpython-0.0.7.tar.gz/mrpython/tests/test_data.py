# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_equal

from mrpython.data import STATES, ORDERED_STATES


def test_states():
    assert_equal(len(STATES), 57)


def test_ordered_states():
    assert_equal(len(ORDERED_STATES), 57)
