"""
Test separable utility functions used in say
"""

import six
from say.util import *


def test_is_string():

    assert is_string("")
    assert is_string("This")
    assert is_string(six.u("this"))
    assert not is_string(1)
    assert not is_string(None)
    assert not is_string([1, 2, 3])
    assert not is_string(['a', 'b', 'c'])


def test_encoded():

    tests = {
        ('this', 'utf-8'): six.b('this'),
        (six.u('this'), 'utf-8'): six.b('this'),
        (six.u('this\u2012and'), 'utf-8'): six.b('this\xe2\x80\x92and'),
        (six.u('this-and'), 'base64'): 'dGhpcy1hbmQ=\n',
    }

    for data, answer in tests.items():
        (text, encoding) = data
        assert encoded(text, encoding) == answer


def test_flatten(*args):

    tests = [
        (1,       [1]),
        ([1],     [1]),
        ('one',   ['one']),
        (['one'], ['one']),
        ([2, 3, 4], [2, 3, 4])

    ]

    for data, answer in tests:
        assert [x for x in flatten(data)] == answer
