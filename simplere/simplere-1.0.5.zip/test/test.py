
from simplere import *
import re

class YesItIs(ValueError): pass

def test_basic():
    tests = 'some string with things in it ok?'
    
    sword  = Re(r'\b(s\w*)\b')    
    
    if tests in sword:
        assert Re._[1] == 'some'
        assert Re._.end(1) == 4
        assert Re._._match.group(1) == Re._[1]
    else:
        raise YesItIs()
    
    assert 'ddd' not in sword
    assert 'it goes other ways' not in sword
    assert 'it goes other ways sometimes' in sword    
    
def test_findall():
    tests = 'some string with things in it ok?'
    
    sword  = Re(r'\b(s\w*)\b')    

    assert sword.findall(tests) == ['some', 'string']
    
    iterlist = [ m[1] for m in sword.finditer(tests) ]
    assert iterlist == ['some', 'string']
    
def test_attributes():
    
    tests = 'some string with things in it ok?'
    sword  = Re(r'\b(?P<word>s\w*)\b')
    
    if tests in sword:
        assert Re._.word == 'some'
    else:
        raise YesItIs()
    
    iterlist = [ m.word for m in sword.finditer(tests) ]
    assert iterlist == ['some', 'string']

    person = 'John Smith 48'
    if person in Re(r'(?P<name>[\w\s]*)\s+(?P<age>\d+)'):
        assert Re._.name == 'John Smith'
        assert int(Re._.age) == 48
        assert Re._.name == Re._._match.group('name')
        assert Re._.age  == Re._._match.group('age')
    else:
        raise YesItIs()
    
    for found in Re(r'pattern (\w+)').finditer('pattern is as pattern does'):
        assert isinstance(found, ReMatch)
        assert found[1] in ['is','does']
    
    found = Re(r'pattern (\w+)').findall('pattern is as pattern does')
    assert found == 'is does'.split()
    
def test_regrouping():
    sentence = "you've been a bad boy"
    pattern = r'(?P<word>bad)'
    re_pat = Re(pattern)
    
    repl = lambda m: m.word.upper() # note use of attributes
    
    newsent = re_pat.sub(repl, sentence)
    assert newsent == "you've been a BAD boy"
    
    sentcap = Re(r'^(?P<first>.)')
    sentcap_repl = lambda m: m.first.upper()
    
    assert sentcap.sub(sentcap_repl, newsent) == "You've been a BAD boy"
    
    
def test_memoization():    
    testpat  = Re(r'\b(s\w*)\b')
    testpat1 = Re(r'\b(s\w*)\b')
    assert testpat is testpat1   # test memoization
    
    assert Glob('a*') is Glob('a*')
    
def test_from_sre():
    pat = re.compile(r'\b(s\w*)\b')
    repat = Re(pat)
    
    tests = 'some string with things in it ok?'
    assert tests in repat
    assert repat.findall(tests) == ['some', 'string']
    
    assert 'ddd' not in repat
    
def test_direct_ReMatch():
    
    m = re.match(r'this', 'that')
    assert not m
    assert not ReMatch(m)
    
    m = re.match(r'this', 'this')
    assert m
    assert ReMatch(m)

    
def test_direct_ReMatch_easy_access():
    m = re.match(r'this', 'this')
    rm = ReMatch(m)
    assert m.group(0) == 'this'
    assert rm.group(0) == 'this'

    match = re.match(r'(?P<word>this)', 'this is a string')
    match = ReMatch(match)
    assert match[1] == match.word
    assert match.group(1) == match.word

def test_en_passant_Match():
    s = 'this is the test of that thing you like'
    
    match  = Match()
    
    if match / re.search(r'th\w*', s):
        assert match[0] == 'this'
    else:
        assert YesItIs()

    if match < re.search(r'th\w*', s):
        assert match[0] == 'this'
    else:
        assert YesItIs()
        
    if match <= re.search(r'th\w*', s):
        assert match[0] == 'this'
    else:
        assert YesItIs()
        
    if match / re.search(r'(?P<target>th\w+g)', s):
        assert match.target == 'thing'
        
    # from the docs
    if match / re.search(r'(?P<word>th.s)', 'this is a string'):
        assert match[1] == 'this'
        assert match.word == 'this'
        assert match.group(1) == 'this'

    if match < Re(r'(?P<word>th..)').search('and that goes there'):
        assert match.word == 'that'
        
    answer = Match()   # need to do this just once
    
    if answer < Re(r'(?P<word>th..)').search('and that goes there'):
        assert answer.word == 'that'


def test_en_passant_with_Re():
    """
    Make sure that if ReMatch object already generated, that
    en passant usage understands that.
    """
    
    match = Match()
    s = 'this is the test of that thing you like'

    if match / Re(r'thi\w+').search(s):
        assert match[0] == 'this'
    

def test_Glob():
    assert "alpha" in Glob("a*")
    assert "beta" not in Glob("a*")
    
    assert 'globtastic' in Glob('glob*')
