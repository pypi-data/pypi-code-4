from fanery.librand import *
from fanery.terms import *

def test_hict():
    d = hict(n = randnum())
    assert d.n is d['n']
    assert isinstance(d.n, (int, long, Decimal))
    assert is_dict(d.d)
    assert is_dict(d.d.d)
    assert is_dict(d.d.d.d)
    s = ('2012-01-01', '1.0', '1')
    d.s = s
    assert is_date(d.s[0]), d
    assert is_number(d.s[1]), d
    assert is_number(d.s[2]), d
    d.setdefault('n', '2000-01-01')
    assert is_number(d.n)
    d.update(n = '2000-01-01', n02 = 'Nov 02')
    assert is_date(d.n)
    assert d.n is d['n']
    assert is_date(d.n02), d
    assert d.n02.month is 11 and d.n02.day is 2
    assert d.update(e = 1.0).update(f = 1) is d
    assert d.e is d.f is 1
