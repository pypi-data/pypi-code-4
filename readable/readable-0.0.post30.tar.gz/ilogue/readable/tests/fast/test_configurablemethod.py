#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock, sentinel
from ilogue.readable import setupMethod


class ConfigurableMethodTestCase(unittest.TestCase):

    def test_setupMethod_toReturnInOrder_returns_arguments_in_order(self):
        myMethod = Mock()
        valuesToReturn = [
            sentinel.first,
            "second",
            333]
        setupMethod(myMethod).toReturnInOrder(*valuesToReturn)
        self.assertEqual(myMethod(), sentinel.first)
        self.assertEqual(myMethod(), "second")
        self.assertEqual(myMethod(), 333)


if __name__ == '__main__':
    unittest.main()
