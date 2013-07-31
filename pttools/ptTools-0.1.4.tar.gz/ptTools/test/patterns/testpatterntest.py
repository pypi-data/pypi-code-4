#!/usr/bin/env python3

import unittest

from ptTools.patterns import TestPattern as Test

from . import AbstractPatternTest


class TestPatternTest(AbstractPatternTest):

    def test_match(self):
        iseven = lambda n : n % 2 == 0
        self.assertMatch(2, Test(iseven))
        self.denyMatch(3, Test(iseven))


if __name__ == '__main__':

    unittest.main()
