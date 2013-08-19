
import six
from namedentities import *
import sys


def _print(*args, **kwargs):
    """
    Python 2 and 3 compatible print function, similar to Python 3 arg handling.
    """
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    f   = kwargs.get('file', sys.stdout)
    parts.append(end)
    f.write(sep.join(parts))
    
def test_unicode():
    u = six.u('both em\u2014and')
    assert named_entities(u) == six.u("both em&mdash;and")

def test_numeric_entity():
    u = six.u('and&#x2013;dashes')
    assert named_entities(u) == six.u("and&ndash;dashes")
    
def test_hex():
    u = six.u('both em\u2014and&#x2013;dashes&hellip;')
    assert hex_entities(u) == six.u("both em&#x2014;and&#x2013;dashes&#x2026;")

def test_unicode_and_numeric():
    u = six.u('both em\u2014and&#x2013;dashes&hellip;')
    assert named_entities(u) == six.u("both em&mdash;and&ndash;dashes&hellip;")


def test_six_print_example(capsys):
    u = six.u('both em\u2014and&#x2013;dashes&hellip;')
    six.print_(named_entities(u))
    out, err = capsys.readouterr()
    assert out.startswith("both em&mdash;and&ndash;dashes&hellip;")
    
def test_docs_example():    
    u = six.u('both em\u2014and&#x2013;dashes&hellip;')
    assert named_entities(u)   == 'both em&mdash;and&ndash;dashes&hellip;'
    assert numeric_entities(u) == 'both em&#8212;and&#8211;dashes&#8230;'
    assert unescape(u)   == six.u('both em\u2014and\u2013dashes\u2026')
