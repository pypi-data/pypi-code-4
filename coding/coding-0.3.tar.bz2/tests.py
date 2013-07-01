#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <28-Dec-2010 18:26:59 PST by rich@noir.com>

"""
Tests for the Coding class.
"""

from __future__ import unicode_literals, print_function

__docformat__ = 'restructuredtext en'

import coding

import nose
from nose.tools import assert_true, assert_false, assert_equal, assert_raises, raises

### uncomment these for verbose logging
# import logging
# logger = logging.getLogger()
# handler = logging.StreamHandler()
# handler.setLevel(rcmp.INDETERMINATES)
# logger.addHandler(handler)

peopleData = [
    ('Bob', 1, 'This code represents Bob.'),
    ('Carol', 2, 'Carol represented here'),
    ('Ted', 3, 'Better Ted than Fred'),
    ('Alice', 5, 'Doesn\'t live here anymore'),
    ]

peopleDups = [
    ('Carol', 4, 'Duplicate Carol entry'),
    ('George', 2, 'Duplicate code 2'),
    ]    

class PeopleCoding(coding.Coding):
    overload_codes = True
    overload_names = True
    byname = bycode = {}

class PeopleNameMajor(coding.NameMajorCoding):
    overload_codes = True
    overload_names = True
    byname = bycode = {}

class PeopleCodeMajor(coding.CodeMajorCoding):
    overload_codes = True
    overload_names = True
    byname = bycode = {}

class PeopleNameMajorDups(coding.NameMajorCoding):
    overload_codes = True
    overload_names = True
    byname = bycode = {}

class PeopleCodeMajorDups(coding.CodeMajorCoding):
    overload_codes = True
    overload_names = True
    byname = bycode = {}

def setUp():
    for i in peopleData:
        PeopleCoding(i[0], i[1], i[2])
        PeopleNameMajor(i[0], i[1], i[2])
        PeopleCodeMajor(i[0], i[1], i[2])
        PeopleNameMajorDups(i[0], i[1], i[2])
        PeopleCodeMajorDups(i[0], i[1], i[2])

    for i in peopleDups:
        PeopleNameMajorDups(i[0], i[1], i[2])
        PeopleCodeMajorDups(i[0], i[1], i[2])

def testSome():
    for cls in [PeopleCoding, PeopleNameMajor, PeopleCodeMajor]:
        def testByname():
            for i in peopleData:
                x = cls.byname[i[0]]
                assert_equal(x.name, i[0])
                assert_equal(x.code, i[1])
                assert_equal(x.closure, i[2])

        yield(testByname)

        def testBycode():
            for i in peopleData:
                x = cls.bycode[i[1]]
                assert_equal(x.name, i[0])
                assert_equal(x.code, i[1])
                assert_equal(x.closure, i[2])

        yield(testBycode)

        def testConversions():
            for i in peopleData:
                x = cls.bycode[i[1]]
                assert_equal(int(x), x.code)
                assert_equal(str(x), x.name)
                assert_equal(x(), x.closure)

        yield(testConversions)

def testLT():
    x = PeopleNameMajorDups.bycode[5]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        assert_true(x.name == i.name or x < i)

    x = PeopleCodeMajorDups.byname['Bob']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true(x.code == i.code or x < i)

def testLE():
    x = PeopleNameMajorDups.bycode[5]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        assert_true(x.name == i.name or x <= i)

    x = PeopleCodeMajorDups.byname['Bob']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true(x.code == i.code or x <= i)

def testGT():
    x = PeopleNameMajorDups.bycode[3]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        print('x is {0} and i is {1}'.format(str(x), str(i)))
        assert_true(x.name == i.name or x > i)

    x = PeopleCodeMajorDups.byname['Alice']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true(x.code == i.code or x > i)

def testGE():
    x = PeopleNameMajorDups.bycode[3]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        print('x is {0} and i is {1}'.format(str(x), str(i)))
        assert_true(x.name == i.name or x >= i)

    x = PeopleCodeMajorDups.byname['Alice']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true(x.code == i.code or x >= i)

def testEQ():
    x = PeopleNameMajorDups.bycode[3]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        print('x is {0} and i is {1}'.format(str(x), str(i)))
        assert_true((x.name == i.name
                     and x.code == i.code)
                    == (x == i))

    x = PeopleCodeMajorDups.byname['Alice']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true((x.name == i.name
                     and x.code == i.code)
                    == (x == i))

def testNE():
    x = PeopleNameMajorDups.bycode[3]
    for i in [PeopleNameMajorDups.byname[name] for name in PeopleNameMajorDups.byname]:
        print('x is {0} and i is {1}'.format(str(x), str(i)))
        assert_true((x.name != i.name
                     or x.code != i.code)
                    == (x != i))

    x = PeopleCodeMajorDups.byname['Alice']
    for i in [PeopleCodeMajorDups.bycode[code] for code in PeopleCodeMajorDups.bycode]:
        print('x is {0} and i is {1}'.format(int(x), int(i)))
        assert_true((x.name != i.name
                     or x.code != i.code)
                    == (x != i))

if __name__ == '__main__':
    nose.main()
