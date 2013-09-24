#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# tests for the machines class

import unittest
from mock import Mock
from ilogue.readable import assertionMethod

class AssertableResponseTestCase(unittest.TestCase):

    def test_WithPropertyAndValue_should_use_passed_matcher(self):
        from ilogue.readable.assertableobject import AssertableObject
        obj = AssertableObject('some_object')
        (assertionMethod(obj.hasValue)
            .doesNotFailIfPassedMatchingMatcher()
            .failsWithAppropriateMessageIfPassedNonMatchingMatcher())


if __name__ == '__main__':
    unittest.main()
