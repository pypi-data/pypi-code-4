import six
import os
from say import Text
from say.textrange import TextRange


def test_basic():
    t = Text('a\nb\nc\nd')
    assert t.lines == 'a b c d'.split()

    tr = TextRange(t, 1, 3)
    assert tr.text == 'b\nc'
    assert tr.lines == ['b', 'c']

    tr += 'hey!'
    assert t.lines == 'a b c hey! d'.split()

    assert tr.text == 'b\nc\nhey!'
    assert tr.lines == ['b', 'c', 'hey!']


def test_indexing():

    t = Text('a\nb\nc\nd')
    assert t.lines == 'a b c d'.split()

    tr = TextRange(t, 1, 3)
    assert tr.text == 'b\nc'
    assert tr.lines == ['b', 'c']

    assert tr[0] == 'b'
    assert tr[1] == 'c'

    from pytest import raises

    with raises(IndexError):
        assert tr[2] == 'd'


def test_replace():
    t = Text('a\na\na\nb\na')
    assert t.lines == 'a a a b a'.split()

    tr = TextRange(t, 2, 4)
    assert tr.lines == 'a b'.split()

    tr.replace('a', 'A')
    assert tr.lines == 'A b'.split()
    assert t.lines == 'a a A b a'.split()


def test_replace_many():
    t = Text('a\na\na\nb\na')
    assert t.lines == 'a a a b a'.split()

    tr = TextRange(t, 2, 4)
    assert tr.lines == 'a b'.split()

    tr.replace({'a': 'A', 'b': 'BEE'})
    assert tr.lines == 'A BEE'.split()
    assert t.lines == 'a a A BEE a'.split()


def test_re_replace():
    t = Text('a\na\na\nb\na')
    assert t.lines == 'a a a b a'.split()

    tr = TextRange(t, 2, 4)
    assert tr.lines == 'a b'.split()

    tr.re_replace(r'[b]', 'B')
    tr.re_replace(r'a', lambda m: m.group(0).upper())
    assert t.lines == 'a a A B a'.split()


def test_interpolation():
    x = 21
    t = Text("Joe,\nthis is {x}")
    assert t.text == 'Joe,\nthis is 21'

    tr = TextRange(t, 1, 3)

    tr += 'and {x}'
    assert tr.text == 'this is 21\nand 21'

    tr &= 'and {x}'
    assert tr.text == 'this is 21\nand 21\nand {x}'

    assert t.text == 'Joe,\nthis is 21\nand 21\nand {x}'


def test_replace():
    t = Text('a\nb\nc\nd')
    assert t.lines == 'a b c d'.split()
    tr = TextRange(t, 1, 3)
    assert tr.lines == ['b', 'c']

    tr.replace('b', 'B')
    assert tr.lines == ['B', 'c']
