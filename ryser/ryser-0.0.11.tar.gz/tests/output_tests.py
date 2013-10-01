# Copyright Matthew Henderson 2013.
# Created 18.12.2010 (Chandlers Ford). Last updated Fri Sep 13 17:15:35 BST 2013

import unittest
import ryser.designs

from ryser.utils import from_file

from ryser.output import dict_to_string, dict_to_string_simple, row_string

from ryser.examples import eg1

class TestRowString(unittest.TestCase):
    """Testing of row to string."""

    def setUp(self):
        pass

    def test_row_string(self):
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 0),'|.|.|7|3|5|.|.|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 1),'|.|.|.|.|6|1|5|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 2),'|.|6|.|.|.|.|3|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 3),'|6|.|.|.|.|.|.|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 4),'|4|.|.|.|.|.|.|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 5),'|2|.|1|.|.|.|.|')
        self.assertEqual(row_string(eg1.fixed_cells(), 7, 6),'|3|4|2|.|.|.|.|')

class TestDictToString(unittest.TestCase):
    """Testing of string conversion."""

    def setUp(self):
        pass

    def test_dict_to_string(self):
        pass

class TestDictToStringSimple(unittest.TestCase):
    """Testing of string conversion."""

    def setUp(self):
        pass

    def test_dict_to_string_simple(self):
        self.assertEqual(dict_to_string_simple(eg1.fixed_cells(), 7),'|.|.|7|3|5|.|.|\n|.|.|.|.|6|1|5|\n|.|6|.|.|.|.|3|\n|6|.|.|.|.|.|.|\n|4|.|.|.|.|.|.|\n|2|.|1|.|.|.|.|\n|3|4|2|.|.|.|.|')
