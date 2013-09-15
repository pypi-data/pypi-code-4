from ..pyquchk import *
from ..pyquchk.arbitraries import *


def test_simple_true():
    assert for_all(lambda x: x * 2 / 2 == x, x=int_)


def test_simple_false():
    assert not for_all(lambda x: x * 3 / 2 == x, x=int_)
