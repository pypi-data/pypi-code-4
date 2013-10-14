# -*- coding: utf8 -*-
from . import TestCase

class Subject(object):
    args = tuple()
    kwargs = dict()
    def __call__(self, event):
        self.args = event.args
        self.kwargs = event.kwargs
        event.result = False

class EventData(object):
    name = 'event'
    subject = Subject()
    args = tuple()
    kwargs = dict()
    result = True

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

class DocExamplesTest(TestCase):
    def test_operators(self):
        from inxpect.expect.operator import Equal
        from inxpect import And, Or

        equal_2 = Equal(2)
        assert  equal_2(2)
        assert equal_2(3) is False

        assert Equal.is_true(2, 2)
        assert Equal.is_false(2, 3)

        # You can use a getter function:
        mod_3 = lambda num: num % 3
        multiple_of_3 = Equal(0, mod_3)

        assert multiple_of_3(15)
        assert multiple_of_3(16) is False

        # chaining:
        mod_5 = lambda num: num % 5
        multiple_of_5 = Equal(0, mod_5)

        multiple_of_3_and_5 = And(multiple_of_3, multiple_of_5)
        multiple_of_3_or_5 = Or(multiple_of_3, multiple_of_5)

        assert multiple_of_3_and_5(15)
        assert multiple_of_3_or_5(16) is False

        multiple_of_4 = Equal(0, lambda num: num % 4)

        multiple_of_3_4_or_5 = multiple_of_3_or_5 | multiple_of_4

        assert multiple_of_3_4_or_5(16)

        # Testing and search (lambda is partially pickled):
        assert (multiple_of_5 == Equal(0, lambda num: num % 5))
        assert (multiple_of_5 == Equal(0, lambda num: num % 4)) is False


    def test_Inspect(self):
        import inxpect

        expect = inxpect.expect_factory(EventData)
        assert hasattr(expect, 'result')
        assert hasattr(expect.subject, 'args') is False
        # with depth to 1:
        expect = inxpect.expect_factory(EventData, 1)
        assert hasattr(expect.subject, 'args')

    def test_Expect_basics(self):
        import inxpect

        expect = inxpect.expect_factory(EventData)

        name_is_event1 = expect.name.equal_to('event1')  # can be done with ==
        result_is_not_None = expect.result != None
        is_event1 = name_is_event1 & result_is_not_None

        event1 = EventData(name='event1')
        event2 = EventData(name='event2', result=None)

        assert result_is_not_None(event1)
        assert result_is_not_None(event2) is False

        assert name_is_event1(event1)
        assert name_is_event1(event2) is False

        log = []
        expected = 'Name %s is not "event1"'

        def is_event1_fails(chain, at, *args, **kwargs):
            # args and kwargs are same passed to is_event1:
            event = args[0]
            if at in expect.name.equal_to('event1'):
                log.append(expected % event.name)
            return False

        is_event1.on_fail(is_event1_fails)

        assert is_event1(event1)
        assert is_event1(event2) is False

        assert log[0] == expected % 'event2'


    def test_Expect_closures(self):
        import inxpect

        expect = inxpect.expect_factory(EventData)

        name_len_is_5 = expect.name.equal_to(5, len)

        event1 = EventData()
        event2 = EventData(name='0123456789')

        assert name_len_is_5(event1)
        assert name_len_is_5(event2) is False

        # the closure also encapsulate len for comparisons
        assert name_len_is_5 == expect.name.equal_to(5, len)

        ### Details:
        # Never use this but it shows how len is encapsulated

        # func is the internal varname, needed to compare bytecode
        func = len
        # Lambda permit to get bytecode from __code__ attibute
        func_len = lambda *args, **kwargs: func(*args, **kwargs)
        not_func_len = lambda *args, **kwargs: len(*args, **kwargs)

        assert (name_len_is_5 == expect.name.equal_to(5, func_len))
        # assert it compares bytecode
        assert (name_len_is_5 == expect.name.equal_to(5, not_func_len)) is False


    def test_Expect_should(self):
        from inxpect.expect import Expect
        from inxpect.expect.operator import Operator

        class MultipleOf5(Operator):
            @classmethod
            def is_true(cls, given, expected):
                return given % 5 == expected


        expect = Expect()
        expected = 0
        multiple_of_5 = expect.should(MultipleOf5, expected)

        assert multiple_of_5(10)
        assert multiple_of_5(11) is False

        # Should provides also the negation:
        not_multiple_of_5 = expect.should_not(MultipleOf5, expected)

        assert not_multiple_of_5(11)


        # Should can take closure:
        divide_by_2 = lambda given: given / 2
        multiple_of_2_and_5 = expect.should(MultipleOf5, expected, divide_by_2)

        assert multiple_of_2_and_5(10)
        assert multiple_of_2_and_5(15) is False

        # Should syntactic sugar:
        is_10 = expect.should == 10
        assert is_10(10)
        assert is_10(11) is False
        # like expect:
        is_10 = expect == 10
        assert is_10(10)
        assert is_10(11) is False

        # at the difference that should can take a closure:
        mod_2 = lambda num: num % 2
        multiple_of_2 = expect.should == (0, mod_2)
        assert multiple_of_2(10)
        assert multiple_of_2(11) is False

        # unlike expect:
        weird_example = expect == (0, mod_2)
        assert weird_example(10) is False
        assert weird_example((0, mod_2))

