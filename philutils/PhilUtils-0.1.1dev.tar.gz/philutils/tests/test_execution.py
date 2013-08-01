#!/usr/bin/env python

#Name: test_execution.py
#Author: Philip Zerull
#Date Created: Thursday July 25, 2013


import os
import sys
import unittest
from philutils import execution


def square(x):
    return poly(x, 2)


def cube(x):
    return poly(x, 3)


def supercube(x):
    return poly(x, 4)


def poly(x, n):
    return x**n


def raises(x):
    raise Exception("the value x is '%s'" % x)


class TestExecution(unittest.TestCase):
    def test_that_job_returns_correct_result(self):
        runner = execution.Job(square, 5)
        result = runner.finish()['value']
        expected = square(5)
        self.assertEqual(result, expected)

    def test_that_job_returns_correct_status(self):
        runner = execution.Job(square, 5)
        result = runner.finish()['status']
        self.assertEqual(result, 'success')

    def test_running_multiple_functions(self):
        runner = execution.run_multiple_functions
        results = runner([square, cube, supercube], 6)
        self.assertEqual(results, [36, 216, 1296])

    def test_error_returns_correct_status(self):
        runner = execution.Job(raises, 'monkey')
        result = runner.finish()['status']
        self.assertEqual(result, 'error')

    def test_error_returns_correct_error_type(self):
        runner = execution.Job(raises, 'monkey')
        result = runner.finish()['value']['exc_info'][1]
        self.assertIsInstance(result, Exception)

    def test_error_returns_string_traceback(self):
        runner = execution.Job(raises, 'monkey')
        result = runner.finish()['value']['exc_info'][2]
        self.assertIsInstance(result, str)

