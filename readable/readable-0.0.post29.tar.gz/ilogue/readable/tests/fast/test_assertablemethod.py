#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# tests for the machines class

import unittest
from mock import Mock, sentinel
from ilogue.readable import assertMethod
from ilogue.readable.matcher import Matcher


class AssertableMethodTestCase(unittest.TestCase):

    def assertMethodWasCalledExactlyOnceThrowsFor(self, aMethod):
        try:
            assertMethod(aMethod).wasCalled().exactlyOnce()
        except AssertionError:
            return True
        else:
            return False

    def test_passing_Matcher_to_withArgument_matches_it(self):
        myMethod = Mock()
        matcherMock = Matcher()
        matcherMock.matches = Mock()
        myMethod(sentinel.something)
        # run
        try:
            (assertMethod(myMethod).wasCalled()
                .withArgument(matcherMock))
        except AssertionError:
            pass
        #assert
        assert matcherMock.matches.called, "Matcher.matches wasn't called."

    def test_exactlyOnce_asserts_number_of_calls(self):
        myMethod = Mock()
        onZeroCalls = self.assertMethodWasCalledExactlyOnceThrowsFor(myMethod)
        myMethod()  # once
        onOneCall = self.assertMethodWasCalledExactlyOnceThrowsFor(myMethod)
        myMethod()  # twice
        onTwoCalls = self.assertMethodWasCalledExactlyOnceThrowsFor(myMethod)
        prefix = "AssertableMethod.exactlyOnce"
        self.assertTrue(onZeroCalls, prefix + " didnt fail on zero calls.")
        self.assertFalse(onOneCall, prefix + " failed on one calls.")
        self.assertTrue(onTwoCalls, prefix + " didnt fail on two calls.")


if __name__ == '__main__':
    unittest.main()
