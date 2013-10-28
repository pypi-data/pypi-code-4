#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import dwarf
import unittest

class DwarfTestCase(unittest.TestCase):

    def setUp(self):
        dwarf.app.config.from_object('config.TestingConfig')
        self.app = dwarf.app.test_client()

    def tearDown(self):
        pass

    def test_basic_addition(self):
        self.assertEqual(5, 6, 'obviously')


if __name__ == '__main__':
    unittest.main()
