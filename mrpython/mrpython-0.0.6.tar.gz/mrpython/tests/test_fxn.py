# -*- coding: utf-8 -*-

import logging

from nose.tools.trivial import assert_equal, assert_true

from mrpython.fxn import autolog, enum, ip2long, long2ip

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
	assert_equal(l, 4294967040L)

def test_long2ip():
	l = 4294967040L
	ip = long2ip(l)
	assert_equal(ip, '255.255.255.0')