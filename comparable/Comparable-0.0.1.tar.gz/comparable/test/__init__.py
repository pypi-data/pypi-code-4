#!/usr/bin/env python

"""
Tests for comparable package.
"""

import logging
import unittest


class TestCase(unittest.TestCase):  # pylint: disable=R0904
    """Common test case class with new assertion methods."""  # pylint: disable=C0103

    def assertComparison(self, obj1, obj2, expected_equality, expected_similarity):  # pylint:disable=R0913
        """Fail if objects do not match the expected equality and similarity.
        """
        logging.info("calculating equality...")
        equality = obj1 == obj2
        logging.info("calculating similarity...")
        similarity = obj1 % obj2
        logging.info("checking expected results...")
        self.assertEqual(expected_equality, equality)
        self.assertAlmostEqual(expected_similarity, similarity, 2)
