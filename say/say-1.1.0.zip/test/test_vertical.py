
from say.vertical import *
import pytest

def test_basic():
    assert Vertical(0,0).render() == ([], [])
    assert Vertical(1,1).render() == ([''], [''])
    assert Vertical(1,2).render() == ([''], ['', ''])
    assert Vertical(2,1).render() == (['', ''], [''])
    assert Vertical(2,3).render() == (['', ''], ['', '', ''])

def test_strings():
    assert Vertical(0,0,'x','y').render() == ([], [])
    assert Vertical(1,1,'x','y').render() == (['x'], ['y'])
    assert Vertical(1,2,'x','y').render() == (['x'], ['y', 'y'])
    assert Vertical(2,1,'x','y').render() == (['x', 'x'], ['y'])
    assert Vertical(2,3,'x','y').render() == (['x', 'x'], ['y', 'y', 'y'])
    assert Vertical(2,0,'x','y').render() == (['x', 'x'], [])
    assert Vertical(0,3,'x','y').render() == ([], ['y', 'y', 'y'])

def test_memoization():
    assert Vertical(0,0,'x','y') is Vertical(0,0,'x','y')
    assert Vertical(0,3,'x','y') is Vertical(0,3,'x','y')
    assert Vertical(before=1, after=1, bstr='', astr='') is Vertical(before=1, after=1, bstr='', astr='')

@pytest.mark.skipif('True')
def test_vertical():
    assert vertical() is vertical(0)
    assert vertical(0) is Vertical(0,0,'','')
    assert vertical(1) is Vertical(1,1,'','')
    assert vertical(1,2) is Vertical(1,2,'','')
