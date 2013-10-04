#!/usr/bin/env python

"""
Tests for the comparable.tools module.
"""

import logging
import unittest

from comparable.simple import Number
from comparable import tools

from comparable.test import TestCase, settings


class TestEqual(TestCase):  # pylint: disable=R0904
    """Integration tests for equality functions."""

    items = [Number(42), Number(42.001), Number(43)]

    def test_find_equal(self):
        """Verify equal items can be found."""
        base = Number(42)
        gen = tools.find_equal(base, self.items)
        self.assertListEqual([Number(42)], list(gen))

    def test_find_equal_none(self):
        """Verify an empty generator when no items can be found."""
        base = Number(41)
        gen = tools.find_equal(base, self.items)
        self.assertListEqual([], list(gen))

    def test_match_equal(self):
        """Verify an equal item can be matched."""
        base = Number(42)
        item = tools.match_equal(base, self.items)
        self.assertEqual(Number(42), item)

    def test_match_equal_none(self):
        """Verify None is return when no equal item."""
        base = Number(41)
        item = tools.match_equal(base, self.items)
        self.assertEqual(None, item)


class TestSimilar(TestCase):  # pylint: disable=R0904
    """Integration tests for similarity functions."""

    items = [Number(42), Number(42.001), Number(43)]

    def test_find_similar(self):
        """Verify similar items can be found."""
        base = Number(42)
        gen = tools.find_similar(base, self.items)
        self.assertListEqual([Number(42), Number(42.001)], list(gen))

    def test_find_similar_none(self):
        """Verify an empty generator when no items can be found."""
        base = Number(41)
        gen = tools.find_similar(base, self.items)
        self.assertListEqual([], list(gen))

    def test_match_similar(self):
        """Verify an similar item can be matched."""
        base = Number(42)
        item = tools.match_similar(base, self.items)
        self.assertEqual(Number(42), item)

    def test_match_similar_none(self):
        """Verify None is return when no similar item."""
        base = Number(41)
        item = tools.match_similar(base, self.items)
        self.assertEqual(None, item)


class TestDuplicates(TestCase):  # pylint: disable=R0904
    """Integration tests for duplicate functions."""

    items = [Number(42), Number(42.001), Number(43)]

    def test_duplicates(self):
        """Verify duplicate items can be found."""
        base = Number(42)
        gen = tools.duplicates(base, self.items)
        self.assertListEqual([Number(42.001)], list(gen))


class TestSort(TestCase):  # pylint: disable=R0904
    """Integration tests for sort functions."""

    items = [Number(42), Number(42.001), Number(43)]

    def test_sort(self):
        """Verify items can be sorted."""
        base = Number(42.001)
        items = tools.sort(base, self.items)
        self.assertListEqual([Number(42.001), Number(42), Number(43)], items)


if __name__ == '__main__':
    logging.basicConfig(format=settings.DEFAULT_LOGGING_FORMAT,
                        level=settings.DEFAULT_LOGGING_LEVEL)
    unittest.main(verbosity=0)
