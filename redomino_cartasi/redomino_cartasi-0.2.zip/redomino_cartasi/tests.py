"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import unittest
import doctest

from django.test import TestCase

from redomino_cartasi import utils


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(utils))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SimpleTest))
    return suite

