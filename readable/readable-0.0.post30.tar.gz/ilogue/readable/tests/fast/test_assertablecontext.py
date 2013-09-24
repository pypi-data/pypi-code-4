#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock, sentinel


class AssertableContextTestCase(unittest.TestCase):

    def test_asserts_entering_context(self):
        from ilogue.readable.ContextProviderMock import ContextProviderMock
        aContextProvider = ContextProviderMock()
        contextNotEntered = self.assertContextThrowsFor(aContextProvider)
        aContextProvider().__enter__()
        contextEntered = self.assertContextThrowsFor(aContextProvider)
        self.assertTrue(contextNotEntered)
        self.assertFalse(contextEntered)

    def test_throws_if_not_provided_contextprovidermock(self):
        from ilogue.readable import assertContext
        self.assertRaises(TypeError,assertContext,Mock())

    def assertContextThrowsFor(self, aContextProvider):
        from ilogue.readable import assertContext
        try:
            assertContext(aContextProvider)
        except AssertionError:
            return True
        else:
            return False



if __name__ == '__main__':
    unittest.main()
