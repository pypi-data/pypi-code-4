# -*- coding: utf-8 -*-

import logging

from nose.tools.trivial import assert_equal

from mrpython.fxn import (autolog, enum, ip2long,
                          long2ip, to_dict, walk)


def test_autolog():
    autolog('Testing logger...')
    autolog('Testing warning', logging.WARNING)


def test_enum():
    e = enum(ONE='one', TWO='two')
    assert_equal(e.ONE, 'one')
    assert_equal(e.TWO, 'two')


def test_ip2long():
    ip = '255.255.255.0'
    l = ip2long(ip)
    assert_equal(l, long(4294967040))


def test_long2ip():
    l = long(4294967040)
    ip = long2ip(l)
    assert_equal(ip, '255.255.255.0')


def test_to_dict():
    class TestGuy(object):

        def __init__(self):
            self.name = 'Fred'
            self.age = 12
            self.country = 'USA'

    t = TestGuy()
    r = to_dict(t)
    assert_equal(r, {'country': 'USA', 'age': 12, 'name': 'Fred'})
    r = to_dict(t, limit=('country'))
    assert_equal(r, {'country': 'USA'})


def test_walk():
    class Graphable(object):
        _dict_attrs = ()

    class Parent(Graphable):

        def __init__(self):
            self.name = 'The Parent Object'
            self.age = 45
            self.children = [Child(self), Child(self)]
            self.friends = []

        def add_friend(self, parent):
            self.friends.append(parent)

    class Child(Graphable):

        def __init__(self, parent):
            self.parent = parent

        @property
        def siblings(self):
            return [c for c in self.parent.children if c is not self]

        @property
        def friends(self):
            return [c for c in [p.children for p in self.parent.friends]]

    class TestLimit(Graphable):

        _dict_attrs = ('name', 'age')

        def __init__(self):
            self.name = 'Bob'
            self.age = 12
            self.country = 'USA'

    p = Parent()
    p.add_friend(Parent())
    p.add_friend(Parent())

    walk(p, graph_interface=Graphable)
    walk(p, graph_max=1, graph_interface=Graphable)

    start_limited = to_dict(p, limit=('name', 'age'))
    walk(start_limited, graph_interface=Graphable)

    walk(TestLimit(), graph_interface=Graphable)
