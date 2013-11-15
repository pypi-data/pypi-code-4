#!/usr/bin/python
# -*- coding: utf-8 -*-


import unittest
from formv.utils import match

class Test(unittest.TestCase):
    def test(self):
        f = ('###-####',
             '(###) ###-####',
             '(###)/###-####',
             '(###)/###-####+###',
             '+1-###-###-####',
             '1-###-###-####',
             '001-###-###-####',
             )

        self.assertTrue(match(f, '123-4567'))
        self.assertTrue(match(f, '(123) 456-7890'))
        self.assertTrue(match(f, '(123)/456-7890'))
        self.assertTrue(match(f, '(123)/456-7890+987'))
        self.assertTrue(match(f, '+1-123-456-7890'))
        self.assertTrue(match(f, '1-123-456-7890'))
        self.assertTrue(match(f, '001-123-456-7890'))
        
        self.assertRaises(ValueError, match, *(f, '0123-4567'))
        self.assertRaises(ValueError, match, *(f, '+(123) 456-7890'))                
        self.assertRaises(ValueError, match, *(f, '(123)-456-7890+987'))