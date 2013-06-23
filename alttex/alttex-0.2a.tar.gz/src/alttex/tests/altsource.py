import nose
from nose.tools import eq_, raises
from alttex.altsource import AltSource, LaTeXError

def alt(src, section='default', values=None):
    'Return a list of alternatives in the given section'
    alt = AltSource(src)
    docs = alt[section]
    if values is None:
        return docs
    else:
        return docs[values]
#===============================================================================
# Basic API
#===============================================================================
def test_sources():
    tex = r'\ALT[foo, bar]{a|b|c}'
    alt = AltSource(tex)
    eq_(sorted(alt.sections()), ['bar', 'default', 'foo'])

#===============================================================================
# the \ALT command
#===============================================================================
def test_basic_alt():
    eq_(alt(r'\ALT{a|b|c}'), ('a', 'b', 'c'))

def test_basic_alt_section():
    eq_(alt(r'\ALT[sec]{a|b|c}'), ('', '', ''))
    eq_(alt(r'\ALT[sec]{a|b|c}', 'sec'), ('a', 'b', 'c'))

def test_alt_section_empty():
    eq_(alt(r'\ALT[sec]{a|b}\ALT{0|1}'), ('0', '1'))
    eq_(alt(r'\ALT[sec]{a|b}\ALT{0|1}', 'sec'), ('a0', 'b1'))

def test_alt_cmd():
    eq_(alt(r'\ALT{a|\b{}}'), ('a', '\\b{}'))

def test_alt_cmd_cmd():
    eq_(alt(r'\ALT{a|\b{\c{d}}}'), ('a', '\\b{\\c{d}}'))

def test_alt_alt_cmd():
    eq_(alt(r'\ALT{a|\ALT{}}'), ('a', '\\ALT{}'))

#===============================================================================
# the \IF command
#===============================================================================
def test_basic_if():
    eq_(alt(r'\IF{sec}{abc}'), ('',))
    eq_(alt(r'\IF{sec}{abc}', 'sec'), ('abc',))

def test_if_cmd():
    eq_(alt(r'\IF{sec}{a\b{}}'), ('',))
    eq_(alt(r'\IF{sec}{a\b{}}', 'sec'), ('a\\b{}',))

@raises(LaTeXError)
def test_if_if_cmd():
    alt(r'\IF{foo,bar}{\IF{foo}{a}b}')

def test_if_alt_cmd():
    eq_(alt(r'\IF{sec}{a\ALT{b|c}}', 'sec'), ('ab', 'ac'))

#===============================================================================
# the \ELSE command
#===============================================================================
def test_basic_else():
    eq_(alt(r'\IF{sec}{abc}\ELSE{cba}'), ('cba',))
    eq_(alt(r'\IF{sec}{abc}\ELSE{cba}', 'sec'), ('abc',))


if __name__ == '__main__':
    nose.runmodule()
