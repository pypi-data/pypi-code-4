# -*- coding: utf8 -*-
from . import TestCase
import inxpect

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

        expect = inxpect.expect_factory(EventData)
        assert hasattr(expect, 'result')
        assert hasattr(expect.subject, 'args') is False
        # with depth to 1:
        expect = inxpect.expect_factory(EventData, 1)
        assert hasattr(expect.subject, 'args')

    def test_Expect_basics(self):

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
