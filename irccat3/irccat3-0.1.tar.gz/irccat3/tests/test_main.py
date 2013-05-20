from __future__ import absolute_import

from nose.tools import eq_

from irccat3 import main

def test_get_args_defaults():
    r = main.get_args([])
    eq_(r.irc_port, 6667)


def test_get_args():
    r = main.get_args(['--irc-port=1234'])
    eq_(r.irc_port, 1234)
