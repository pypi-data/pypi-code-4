#!/usr/bin/env python3

import unittest


class AbstractPatternTest(unittest.TestCase):

    """Abstract class for testing Pattern objects."""

    ## def assertAllMatch(self, obj, patterns):
    ##     """Passes if tuple is matched by all patterns."""        
    ##     for p in patterns:
    ##         self.assertMatch(obj, p)

    ## def denyAnyMatch(self, obj, patterns):
    ##     """Passes if tuple is NOT matched by any pattern."""
    ##     for p in patterns:
    ##         self.denyMatch(obj, p)

    def assertMatch(self, obj, pattern):
        """Passes if tuple is matched by pattern."""
        self.assertTrue(pattern.matches(obj))
        copy = pattern.copy()
        self.assertEquivalentCopy(pattern)

    def denyMatch(self, obj, pattern):
        """Passes if tuple is matched by pattern."""
        self.assertFalse(pattern.matches(obj))
        copy = pattern.copy()
        self.assertEquivalentCopy(pattern)

    def assertEquivalentCopy(self, pattern):
        """Weak assertion of equivalence by print string comparison."""
        cp = pattern.copy()
        self.assertEqual(str(cp), str(pattern))

