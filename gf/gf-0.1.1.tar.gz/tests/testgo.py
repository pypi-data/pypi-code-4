"""Tests for the generic object (`go`) module."""

import sys, os
sys.path.insert(0,
        os.path.abspath(
            os.path.normpath(
                os.path.join(
                    os.path.basename(sys.argv[0]), os.pardir))))
del os, sys

from unittest import TestCase as BaseTestCase
from gf import (Object, Writer, method, 
        __init__, __spy__, __add__, __out__, as_string, spy)



class TestCase(BaseTestCase):
    """The base class of all the tests."""

    def setUp(self):
        """Set up the test class."""

        class TC(Object):
            """A simple test class."""

        @method(TC)
        def __init__(test_object):
            test_object.a0 = "v0"
            test_object.a1 = "v1"
        
        self.TC = TC


class InitTestCase(TestCase):
    """Test the initialisation."""


    def test_init(self):
        """Test the initialisation of our test class."""
        to = self.TC()
        self.failUnlessEqual(to.a0, "v0")
        self.failUnlessEqual(to.a1, "v1")
        self.failUnless(".TC object at" in str(to))


class OutputTestCase(TestCase):
    """Test the output and string conversion functions."""

    def setUp(self):
        """Setup additional output methods."""
        super(OutputTestCase, self).setUp()
        TC = self.TC

        @method(TC, Writer)
        def __out__(test_object, write):
            write("TC(%s, %s)", test_object.a0, test_object.a1)

        @method(TC, Writer)
        def __spy__(self, write):
            __spy__.super(Object, Writer)(self, write)
            write("(")
            __spy__(self.a0, write)
            write(", ")
            __spy__(self.a1, write)
            write(")")

    def test_string_conversion(self):
        """Test the string conversion functions."""
        to = self.TC()
        object_as_string = str(to)
        self.failUnlessEqual(object_as_string, "TC(v0, v1)")
        self.failUnlessEqual(object_as_string, as_string(to))
        debug_string = repr(to)
        self.failUnless(".TC object at" in debug_string)
        self.failUnless(debug_string.endswith(">('v0', 'v1')"))
        self.failUnlessEqual(debug_string, spy(to))


class OperatorTestCase(TestCase):
    """Test a bit of the operators."""

    def setUp(self):
        """Setup additional output methods."""
        super(OperatorTestCase, self).setUp()
        TC = self.TC

        @method(TC, int)
        def __add__(self, an_integer):
            return self.a0 * self.a1 + an_integer

    def test_add(self):
        """Test the newly defined addition method.""" 
        to = self.TC()
        to.a0 = 2
        to.a1 = 3
        self.failUnlessEqual(to + 3, 9)
        self.failUnlessRaises(NotImplementedError, lambda: 3 + to) 


if __name__ == "__main__":
    from unittest import main
    main()
