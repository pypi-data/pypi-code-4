from ..pyquchk import *
from ..pyquchk.arbitrary import Arbitrary
from ..pyquchk.arbitraries import *
from nose.tools import *


@qc
def out_of_class_definition(a=int_):
    eq_(type(a), int)
    assert True


@raises(TypeError)
def test_unbounded_var():
    @qc
    def unbounded_var(self, a=int_):
        pass


@raises(TypeError)
def test_unbounded_var_in_class():
    class test_class:
        @qc
        def unbounded_var(self, a=int_):
            pass


class test_spec_options:
    @qc
    def arb_noparam(a=int_, b=int_):
        eq_(type(a), int)
        eq_(type(b), int)
        eq_(a + b, b + a)

    @qc
    def type_spec(a=int, b=int):
        eq_(type(a), int)
        eq_(type(b), int)
        eq_(a + b, b + a)

    @qc
    def arb_withparam(a=int_(low=1000), b=int_(low=1 << 30)):
        eq_(type(a), int)
        eq_(type(b), int)
        assert a >= 1000
        assert b >= 1 << 30
        eq_(a + b, b + a)


class test_numbers:
    @qc
    def int_add_associativity(a=int, b=int, c=int):
        eq_(a + (b + c), (a + b) + c)

    @raises(AssertionError)
    @qc
    def float_add_associativity(a=float, b=float, c=float):
        eq_(a + (b + c), (a + b) + c)

    @raises(AssertionError)
    @qc
    def float_add_associativity_small_range(a=float_(1, 1.1),
                                            b=float_(1, 1.1),
                                            c=float_(1, 1.1)):
        eq_(a + (b + c), (a + b) + c)

    @raises(AssertionError)
    @qc
    def float_list_sum(a=list_(length=int_(1, 20), elements=float_())):
        eq_(sum(a), sum(reversed(a)))


class test_list:
    @qc
    def int_ops(lst=list_):
        if lst:
            avg_i = sum(lst) / len(lst)
            avg_f = 1.0 * sum(lst) / len(lst)
        assert (len(lst) == 0
                or len(set(lst)) == 1 and min(lst) == avg_i == max(lst)
                or min(lst) < avg_f < max(lst))

    @qc
    def shrink_props(lst=list_, n=int_(0, 5), m=int_(0, 5)):
        shrinked_n = list(list_(length=int_(n, n)).shrink(lst))
        assert all(len(l) == n for l in shrinked_n)

        shrinked_nm = list(list_(length=int_(n, m)).shrink(lst))
        assert all(n <= len(l) <= m for l in shrinked_nm)
