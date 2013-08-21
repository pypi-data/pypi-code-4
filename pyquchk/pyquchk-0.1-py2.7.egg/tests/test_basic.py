from pyquchk import *
from nose.tools import *


@qc
def out_of_class_definition(a=int_):
    eq_(type(a), int)
    assert a + 1


@qc
def arbitrary_empty(a=Arbitrary()):
    assert False


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


class test_edgecases:
    @raises(AssertionError)
    @qc(edgecases=True)
    def edgecases_exist(a=int_):
        assert False

    @raises(AssertionError)
    @qc(edgecases=False)
    def non_edgecases_exist(a=int_):
        assert False

    @qc(edgecases=True)
    def edgecases_values(a=int_(-10, 100)):
        eq_(type(a), int)
        assert a in {-10, 0, 1, 100}

    @raises(AssertionError)
    @qc(edgecases=False)
    def non_edgecases_values(a=int_(-10, 100)):
        assert a in {-10, 0, 1, 100}

    @raises(AssertionError)
    @qc(ntests=0)
    def edgecases_when_ntests0(a=int_):
        assert False

    @qc(ntests=0, edgecases=False)
    def ntests0_and_no_edgecases(a=int_):
        assert False


class test_numbers:
    @raises(AssertionError)
    @qc
    def float_associativity(a=float, b=float, c=float):
        eq_(a + (b + c), (a + b) + c)

    @raises(AssertionError)
    @qc
    def float_list_sum(a=list_(length=int_(1, 20), elements=float_())):
        eq_(sum(a), sum(reversed(a)))


class test_list:
    @qc
    def int_ops(lst=list_):
        assert (len(lst) == 0
                or len(set(lst)) == 1 and min(lst) == sum(lst) / len(lst) == max(lst)
                or min(lst) < sum(lst) / len(lst) < max(lst))

    @qc
    def shrink_props(lst=list_, n=int_(0, 5), m=int_(0, 5)):
        shrinked_n = list(list_(length=int_(n, n)).shrink(lst))
        assert all(len(l) == n for l in shrinked_n)

        shrinked_nm = list(list_(length=int_(n, m)).shrink(lst))
        assert all(n <= len(l) <= m for l in shrinked_nm)

    @raises(AssertionError)
    @qc
    def shrink_props_(lst=list_, n=int_(0, 5)):
        def lsw(**kwargs):
            l = list_(**kwargs)
            return list(l.shrink.__wrapped__(l, lst))

        nshrinked = lsw(length=int_(n, n))
        assert all(len(l) == n for l in nshrinked)
