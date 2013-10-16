
from say.joiner import *
import pytest, sys

### Helper functions

def single(s):
    return "'" + s + "'"

def brackets(s):
    return "[" + s + "]"


### Tests

def test_oxford():
    assert word_join([1,2,3]) == '1, 2, and 3'

def test_heathen():
    assert word_join([1,2,3], lastsep=" and ") == '1, 2 and 3'

def test_quoted():
    assert word_join([], quoter=single) == ""
    assert word_join([1], quoter=single) == "'1'"
    assert word_join([1,2], quoter=single) == "'1' and '2'"
    assert word_join([1,2,3], quoter=single) == "'1', '2', and '3'"

def test_listy():
    assert joiner([], quoter=single, endcaps=brackets) == "[]"
    assert joiner([1], quoter=single, endcaps=brackets) == "['1']"
    assert joiner([1,2], quoter=single, endcaps=brackets) == "['1', '2']"
    assert joiner([1,2,3], quoter=single, endcaps=brackets) == "['1', '2', '3']"

def test_sep():
    assert joiner([], sep='|') == ''
    assert joiner([1], sep='|') == '1'
    assert joiner([1,2], sep='|') == '1|2'
    assert joiner([1,2,3], sep='|') == '1|2|3'

def test_twosep_and_lastsep():
    assert joiner([1,2,3,4], sep='|', lastsep='+') == '1|2|3+4'

    assert joiner([], sep='|', twosep='*', lastsep='+') == ''
    assert joiner([1], sep='|', twosep='*', lastsep='+') == '1'
    assert joiner([1,2], sep='|', twosep='*', lastsep='+') == '1*2'
    assert joiner([1,2,3], sep='|', twosep='*', lastsep='+') == '1|2+3'
    assert joiner([1,2,3,4], sep='|', twosep='*', lastsep='+') == '1|2|3+4'

def test_no_twostep():
    assert joiner([], sep='|', twosep=None, lastsep='+') == ''
    assert joiner([1], sep='|', twosep=None, lastsep='+') == '1'
    assert joiner([1,2], sep='|', twosep=None, lastsep='+') == '1+2'
    assert joiner([1,2,3], sep='|', twosep=None, lastsep='+') == '1|2+3'
    assert joiner([1,2,3,4], sep='|', twosep=None, lastsep='+') == '1|2|3+4'


def test_concat():
    assert concat(4,5,6) == '456'
    # assert concat(range(3)) == '012'
    # assert concat('a','b','c') == 'abc'

def test_and_join():
    assert and_join([]) == ''
    assert and_join([1]) == '1'
    assert and_join([1,2]) == '1 and 2'
    assert and_join([1,2,3]) == '1, 2, and 3'
    assert and_join([1,2,3,4]) == '1, 2, 3, and 4'

def test_or_join():
    assert or_join([]) == ''
    assert or_join([1]) == '1'
    assert or_join([1,2]) == '1 or 2'
    assert or_join([1,2,3]) == '1, 2, or 3'
    assert or_join([1,2,3,4]) == '1, 2, 3, or 4'

def test_items():
    assert items([1,2,3,'string']) == "0: 1\n1: 2\n2: 3\n3: 'string'"

    assert items([1,2,3,'string'], header="---") == "---\n0: 1\n1: 2\n2: 3\n3: 'string'"
    assert items([1,2,3,'string'], footer="===") == "0: 1\n1: 2\n2: 3\n3: 'string'\n==="
    assert items([1,2,3,'string'], header='---', footer="===") == "---\n0: 1\n1: 2\n2: 3\n3: 'string'\n==="


    try:
        from collections import OrderedDict
        answer = "this: something\nthat: else\nplus: additionally"
    except ImportError:
        OrderedDict = dict # py26
        answer = "this: something\nplus: additionally\nthat: else"
        # output in different order because unordred dict
    od = OrderedDict()
    od['this'] = 'something'
    od['that'] = 'else'
    od['plus'] = 'additionally'

    assert items(od, fmt="{key}: {value}") == answer

    assert items(od, fmt="{key}: {value}", header="KEY: VALUE") == \
        "KEY: VALUE\n" + answer
