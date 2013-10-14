# -*- coding: utf8 -*-
from . import TestCase
from inxpect.expect import getters
from inxpect.expect import pickle23

class GettersTest(TestCase):
    def test_getters_repr_return_cPickle_string(self):
        expected = getters.AsIs('val1')
        given = pickle23.loads(repr(expected))

        self.assertEqual(expected, given)

    def test_getters_can_be_found_in_list(self):
        as_is = [getters.AsIs('val1')]
        self.assertIn(getters.AsIs('val1'), as_is)
