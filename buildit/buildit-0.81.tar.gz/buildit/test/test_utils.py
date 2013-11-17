# -*- coding: utf8 -*-
import pytest
from bld.utils import bold, load_bldfile, ParsingError, is_execattr
from ConfigParser import (SafeConfigParser, MAX_INTERPOLATION_DEPTH, Error,
                          InterpolationDepthError, InterpolationSyntaxError,
                          InterpolationMissingOptionError)


# sample test:
def test_bold():
    assert bold('foo') == '\x1b[01mfoo\x1b[00m'


def test_load_interp_syntaxerr():
    data = '''
[readme.html]
exec = rst2html.py %(deps %me
'''
    with pytest.raises(ParsingError):
        load_bldfile(None, from_string=data)


def test_load_unicode():
    data = '''
[vars]
café = café

[readme.html]
deps = %café.rst
exec = echo %deps
'''
    rules, _ = load_bldfile(None, from_string=data)
    assert rules['readme.html'].deps  == [u'café.rst']


def test_is_execattr():
    tests = [
        'exec',         # Trues
        'preexec',
        'preexec.sh',
        'postexec',
        'postexec.py',
        'exec.sh',
        'exec.py',

        'blah',         # Falses
        'exec.',
        'exec_foo_',
        'execblah',

        'proexec.sh',
        'proexec.',
        'postexecr.sh'
    ]
    results = []
    for text in tests:
        results.append( bool(is_execattr(text)) )

    assert results == [True, True, True, True, True, True, True,
                       False, False, False, False, False, False, False]


def test_extends():
    data = '''
[base]
deps = readme.rst
exec = rm readme.html

[clean]
extends = base
exec = rm -f readme.html # override
'''
    rules, _ = load_bldfile(None, from_string=data)
    assert rules['clean'].deps  == ['readme.rst']
    assert rules['clean']['exec']  == 'rm -f readme.html # override'









