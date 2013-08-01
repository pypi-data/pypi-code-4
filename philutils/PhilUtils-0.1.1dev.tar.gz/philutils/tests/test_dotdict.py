#!/usr/bin/env python

#Name: test_dotdict.py
#Author: Philip Zerull
#Date Created: Thursday April 11, 2013


import os
import sys
import unittest
from philutils.containers import DotDict


class TestDotDict(unittest.TestCase):
    def test_getting_using_dot_notation(self):
        newdict = DotDict(fruit='banana')
        self.assertEqual(newdict.fruit, 'banana')

    def test_getting_using_bracket_notation(self):
        newdict = DotDict(animal='dog')
        self.assertEqual(newdict['animal'], 'dog')

    def test_assignment_using_dot_notation(self):
        newdict = DotDict()
        newdict.utensil = 'fork'
        self.assertEqual(newdict['utensil'], 'fork')

    def test_assignment_using_bracket_notation(self):
        newdict = DotDict()
        newdict['utensil'] = 'knife'
        self.assertEqual(newdict.utensil, 'knife')

    def test_usage_of_key_unusable_by_dot_notation(self):
        newdict = DotDict()
        newdict["can't be|used*"] = 5
        self.assertEqual(newdict["can't be|used*"], 5)

    def test_looping_over_keys_defined_using_dot_notation(self):
        newdict = DotDict(a=1, b=2, c=3)
        for key in newdict:
            self.assertIn(key, ['a', 'b', 'c'])
        for item in ['a', 'b', 'c']:
            self.assertIn(item, newdict)

    def test_assignment_of_reserved_word_doesnt_override_dict_behavior(self):
        newdict = DotDict(items=456)
        result = list(newdict.items())
        self.assertEqual(result, [('items', 456)])

    def test_getting_preset_reserved_word_returns_class_method(self):
        newdict = DotDict(values='morals')
        funk = newdict.values
        self.assertEqual(set(funk()), set(['morals']))

    def test_reserved_word_assignment_accessable_using_bracket_notation(self):
        newdict = DotDict(pop='coke')
        self.assertEqual(newdict['pop'], 'coke')
