#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.utils.encoding import crypt

class Test(unittest.TestCase):
    def test(self):
        h = crypt('dummy')
        self.assertEqual(h, crypt('dummy', h))

        h = crypt('dummy', 'key')
        self.assertEqual(h, crypt('dummy', 'key'))