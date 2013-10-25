# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
from nextversion import nextversion


def test_nextversion_usage():
    next_ver = nextversion('1.0.25')
    eq_(next_ver, '1.0.26')


@parameterized([
    # PEP386-compatible versions
    ('1.0a2.dev456'      , '1.0a2.dev457'),
    ('1.0a2'             , '1.0a3'),
    ('1.0a2.1.dev456'    , '1.0a2.1.dev457'),
    ('1.0a2.1'           , '1.0a2.2'),
    ('1.0b1.dev456'      , '1.0b1.dev457'),
    ('1.0b2'             , '1.0b3'),
    ('1.0b2.post345'     , '1.0b2.post346'),
    ('1.0c1.dev456'      , '1.0c1.dev457'),
    ('1.0c1'             , '1.0c2'),
    ('1.0.dev456'        , '1.0.dev457'),
    ('1.0'               , '1.1'),
    ('1.0.post456.dev34' , '1.0.post456.dev35'),
    ('1.0.post456'       , '1.0.post457'),
    ('1.0.1.a2'          , '1.0.1a3'),

    # PEP386-incompatible versions, but can be normalized
    ('2.4-rc1' , '2.4c2'),
    ('v1.0a2'  , '1.0a3'),

    # PEP386-incompatible versions, and cannot be normalized
    ('foo.1.0', None),

    # too large major version number
    ('10000.0', None),
])
def test_nextversion(cur_ver, expected):
    next_ver = nextversion(cur_ver)
    eq_(next_ver, expected)
