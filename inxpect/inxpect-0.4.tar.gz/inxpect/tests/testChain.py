# -*- coding: utf8 -*-
from . import TestCase, Mock
from inxpect.expect import And, Or


class AndTest(TestCase):
    def test_it_should_call_each_callback_it_contains_until_false(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        callback3 = Mock(return_value=True)
        conditions = And(callback1, callback2, callback3)
        args = ('arg1', 'arg2')
        self.assertFalse(conditions(*args))
        callback1.assert_called_once_with(*args)
        callback2.assert_called_once_with(*args)
        self.assertEqual(callback3.call_count, 0)

    def test_can_chain_conditions_with_bitwise_or(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        cond1 = And(callback1) | And(callback2)
        cond2 = And(callback2) | And(callback1)
        self.assertTrue(cond1())
        self.assertTrue(cond2())

    def test_can_chain_conditions_with_bitwise_and(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        cond1 = And(callback1) & And(callback2)
        cond2 = And(callback2) & And(callback1)
        self.assertFalse(cond1())
        self.assertFalse(cond2())

    def test_can_raises_an_exception_when_fail(self):
        expected = 'it fails'
        def fail(chain, at, *args, **kwargs):
            raise AssertionError('it fails')
        cond = And(Mock(return_value=False))
        cond.on_fail(fail)
        with self.assertRaisesRegex(AssertionError, expected):
            cond()

    def test_can_log_result_when_succeed(self):
        message = "ok with: %s and %s"
        logs = []
        def log(chain, *args, **kwargs):
            logs.append(message %(args, kwargs))
        cond = And(Mock(return_value=True))
        cond.on_success(log)
        expected_logs = [
            message %(tuple(), {}),
            message %(('arg1', 'arg2'), {'kwarg1':'val1'})
        ]
        cond()
        cond('arg1', 'arg2', kwarg1='val1')
        self.assertEqual(logs, expected_logs)

    def test_it_returns_OrCondition_when_chaining_with_bitwise_or(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        condition = And(callback1) | And(callback2)
        self.assertIsInstance(condition, Or)

    def test_it_just_extend_when_chaining_with_bitwise_and(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        condition1 = And(callback1)
        condition2 = condition1 & And(callback2)
        self.assertIs(condition1, condition2)
        self.assertIn(callback2, condition2)



class OrTest(TestCase):
    def test_it_returns_true_at_first_callback_that_returns_true(self):
        callback1 = Mock(return_value=False)
        callback2 = Mock(return_value=True)
        callback3 = Mock(return_value=True)
        conditions = Or(callback1, callback2, callback3)
        args = ('arg1', 'arg2')
        self.assertTrue(conditions(*args))
        callback1.assert_called_once_with(*args)
        callback2.assert_called_once_with(*args)
        self.assertEqual(callback3.call_count, 0)

    def test_it_returns_AndCondition_when_chaining_with_bitwise_and(self):
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        condition = Or(callback1) & Or(callback2)
        self.assertIsInstance(condition, And)

    def test_it_just_extend_when_chaining_with_bitwise_or(self):
        callback1 = Mock(return_value=False)
        callback2 = Mock(return_value=True)
        condition1 = Or(callback1)
        condition2 = condition1 | Or(callback2)
        self.assertIs(condition1, condition2)
        self.assertIn(callback2, condition2)

    def test_it_is_searchable(self):
        from inxpect.expect.operator import Equal
        from inxpect.expect.getters import AsIs
        list1 = [Or(Equal(True, AsIs(True)))]
        self.assertIn(Or(Equal(True, AsIs(True))), list1)



