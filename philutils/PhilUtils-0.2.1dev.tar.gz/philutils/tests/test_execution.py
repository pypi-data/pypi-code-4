#!/usr/bin/env python

# Name: test_execution.py
# Author: Philip Zerull
# Date Created: Thursday July 25, 2013


import os
import sys
import unittest
from philutils import execution


def multiply(first=1, second=0):
    return first * second


def three():
    return 3


def square(x):
    return poly(x, 2)


def cube(x):
    return poly(x, 3)


def supercube(x):
    return poly(x, 4)


def poly(x, n=1):
    return x ** n


def raises(x):
    raise Exception("the value x is '%s'" % x)


class Test_retun_results_or_error(unittest.TestCase):
    def test_that_sucessful_run_with_no_arguments_has_status(self):
        result = execution.return_result_or_error(three)
        self.assertEqual(result['status'], 'success')

    def test_sucessful_run_with_no_arguments_has_correct_value(self):
        result = execution.return_result_or_error(three)
        self.assertEqual(result['value'], 3)

    def test_sucessful_run_with_one_argument_has_status(self):
        result = execution.return_result_or_error(cube, 3)
        self.assertEqual(result['status'], 'success')

    def test_sucessful_run_with_one_argument_has_correct_value(self):
        result = execution.return_result_or_error(cube, 3)
        self.assertEqual(result['value'], 27)

    def test_sucessful_run_with_keyword_arguments_has_status(self):
        result = execution.return_result_or_error(multiply, first=3, second=5)
        self.assertEqual(result['status'], 'success')

    def test_sucessful_run_with_mixed_arguments_has_status(self):
        result = execution.return_result_or_error(multiply, first=3, second=5)
        self.assertEqual(result['value'], 15)

    def test_sucessful_run_with_mixed_arguments_has_value(self):
        result = execution.return_result_or_error(poly, 3, n=5)
        self.assertEqual(result['value'], 243)

    def test_that_failed_run_with_no_arguments_has_status(self):
        result = execution.return_result_or_error(poly)
        self.assertEqual(result['status'], 'error')

    def _check_value_of_failed_run(self, funk, *args, **kwargs):
        result = execution.return_result_or_error(funk, *args, **kwargs)
        exec_info = list(sys.exc_info())
        exec_info[2] = str(exec_info[2])
        the_error = result['value']['exc_info']
        self.assertIsInstance(the_error[1], Exception)

    def test_failed_run_with_no_arguments_has_correct_value(self):
        self._check_value_of_failed_run(poly)

    def test_failed_run_with_one_argument_has_status(self):
        result = execution.return_result_or_error(square, 'banana')
        self.assertEqual(result['status'], 'error')

    def test_failed_run_with_one_argument_has_correct_value(self):
        self._check_value_of_failed_run(square, 'banana')

    def test_failed_run_with_mixed_arguments_has_status(self):
        result = execution.return_result_or_error(square, 'banana')
        self.assertEqual(result['status'], 'error')

    def test_failed_run_with_mixed_arguments_has_value(self):
        self._check_value_of_failed_run(poly, 'orange', n='monkey')

    def test_failed_run_with_keyword_arguments_has_status(self):
        kwargs = dict(first='orange', second='monkey')
        result = execution.return_result_or_error(multiply, **kwargs)
        self.assertEqual(result['status'], 'error')

    def test_failed_run_with_keyword_arguments_has_correct_value(self):
        kwargs = dict(first='orange', second='monkey')
        self._check_value_of_failed_run(multiply, **kwargs)


class TestExecution(unittest.TestCase):
    jobclass = execution.Job

    def test_that_job_returns_correct_result(self):
        runner = self.jobclass(square, 5)
        result = runner.finish()['value']
        expected = square(5)
        self.assertEqual(result, expected)

    def test_that_job_returns_correct_status(self):
        runner = self.jobclass(square, 5)
        result = runner.finish()['status']
        self.assertEqual(result, 'success')

    def test_running_multiple_functions(self):
        runner = execution.run_multiple_functions
        results = runner([square, cube, supercube], 6)
        self.assertEqual(results, [36, 216, 1296])

    def test_error_returns_correct_status(self):
        runner = self.jobclass(raises, 'monkey')
        result = runner.finish()['status']
        self.assertEqual(result, 'error')

    def test_error_returns_correct_error_type(self):
        runner = self.jobclass(raises, 'monkey')
        result = runner.finish()['value']['exc_info'][1]
        self.assertIsInstance(result, Exception)

    def test_error_returns_string_traceback(self):
        runner = self.jobclass(raises, 'monkey')
        result = runner.finish()['value']['exc_info'][2]
        self.assertIsInstance(result, str)


class RunWithMultiple(unittest.TestCase):
    def test_that_run_with_empty_returns_result(self):
        results = execution.run_multiple_args(three)
        self.assertEqual(results, [3])

    def test_that_run_with_non_null_args_returns_result(self):
        arglist = [[1], [2], [3], [4], [5]]
        results = execution.run_multiple_args(square, arglist)
        self.assertEqual(results, [1, 4, 9, 16, 25])

    def test_mixed_args_and_kwargs(self):
        arglist = [[1], [2], [3]]
        kwarglist = [dict(n=5), dict(n=2), dict(n=4)]
        funk = execution.run_multiple_args
        results = funk(poly, arglist, kwarglist)
        self.assertEqual(results, [1, 4, 81])

    def test_with_empty_args_and_nonempty_kwarg(self):
        kwarglist = [dict(x=1), dict(x=4), dict(x=10)]
        funk = execution.run_multiple_args
        results = funk(square, None, kwarglist)
        self.assertEqual(results, [1, 16, 100])


class TestProcessExecution(TestExecution):
    jobclass = execution.ProcessJob
