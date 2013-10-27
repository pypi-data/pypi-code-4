#
# Unit Tests for Python numeric values
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest

try:
    unicode
except:
    long = int
try:
    import numpy
    numpy_available=True
except:
    numpy_available=False

class MyBogusType(object):
    def __init__(self, val=0):
        self.val = float(val)

class MyBogusNumericType(MyBogusType):
    def __add__(self, other):
        return MyBogusNumericType(self.val + float(other))

class Test_value(unittest.TestCase):

    def test_none(self):
        val = None
        self.assertEqual(val, value(val))

    def test_bool(self):
        val = False
        self.assertEqual(val, value(val))

    def test_float(self):
        val = 1.1
        self.assertEqual(val, value(val))

    def test_int(self):
        val = 1
        self.assertEqual(val, value(val))

    def test_long(self):
        val = long(1e10)
        self.assertEqual(val, value(val))

    def test_nan(self):
        val = pyutilib.math.nan
        self.assertEqual(id(val), id(value(val)))

    def test_inf(self):
        val = pyutilib.math.infinity
        self.assertEqual(id(val), id(value(val)))

    def test_string(self):
        val = 'foo'
        self.assertEqual(val, value(val))

    def test_const1(self):
        val = NumericConstant(1.0)
        self.assertEqual(1.0, value(val))

    def test_const2(self):
        val = NumericConstant('foo')
        self.assertEqual('foo', value(val))

    def test_const3(self):
        val = NumericConstant(pyutilib.math.nan)
        self.assertEqual(id(pyutilib.math.nan), id(value(val)))

    def test_const4(self):
        val = NumericConstant(pyutilib.math.infinity)
        self.assertEqual(id(pyutilib.math.infinity), id(value(val)))

    def test_error1(self):
        class A(object): pass
        val = A()
        try:
            value(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_error2(self):
        val = NumericConstant(None)
        try:
            value(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass


class Test_is_constant(unittest.TestCase):

    def test_none(self):
        self.assertTrue(is_constant(None))

    def test_bool(self):
        self.assertTrue(is_constant(True))

    def test_float(self):
        self.assertTrue(is_constant(1.1))

    def test_int(self):
        self.assertTrue(is_constant(1))

    def test_long(self):
        val = long(1e10)
        self.assertTrue(is_constant(val))

    def test_string(self):
        self.assertTrue(is_constant('foo'))

    def test_const1(self):
        val = NumericConstant(1.0)
        self.assertTrue(is_constant(val))

    def test_const2(self):
        val = NumericConstant('foo')
        self.assertTrue(is_constant(val))

    def test_error(self):
        class A(object): pass
        val = A()
        try:
            is_constant(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass


class Test_as_numeric(unittest.TestCase):

    def test_none(self):
        val = None
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_bool(self):
        val = False
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass
        val = True
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_float(self):
        val = 1.1
        self.assertEqual(val, as_numeric(val))

    def test_int(self):
        val = 1
        self.assertEqual(val, as_numeric(val))

    def test_long(self):
        val = long(1e10)
        self.assertEqual(val, as_numeric(val))

    def test_string(self):
        val = 'foo'
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_const1(self):
        val = NumericConstant(1.0)
        self.assertEqual(1.0, as_numeric(val))

    def test_const2(self):
        val = NumericConstant('foo')
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except:
            pass

    def test_error1(self):
        class A(object): pass
        val = A()
        try:
            as_numeric(val)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_error2(self):
        val = NumericConstant(None)
        num = as_numeric(val)
        try:
            value(num)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_unknownType(self):
        ref = MyBogusType(42)
        try:
            val = as_numeric(ref)
            self.fail("Expected ValueError")
        except ValueError:
            pass

    def test_unknownNumericType(self):
        ref = MyBogusNumericType(42)
        val = as_numeric(ref)
        self.assertEqual(val().val, 42)
        from coopr.pyomo.base.numvalue import native_numeric_types, native_types
        self.assertIn(MyBogusNumericType, native_numeric_types)
        self.assertIn(MyBogusNumericType, native_types)
        native_numeric_types.remove(MyBogusNumericType)
        native_types.remove(MyBogusNumericType)

    def test_numpy(self):
        if not numpy_available:
            self.skipTest("This test requires NumPy")
        ref = numpy.float64(42)
        val = as_numeric(ref)
        self.assertEqual(val(), 42)
        from coopr.pyomo.base.numvalue import native_numeric_types, native_types
        self.assertIn(numpy.float64, native_numeric_types)
        self.assertIn(numpy.float64, native_types)
        native_numeric_types.remove(numpy.float64)
        native_types.remove(numpy.float64)


if __name__ == "__main__":
    unittest.main()

