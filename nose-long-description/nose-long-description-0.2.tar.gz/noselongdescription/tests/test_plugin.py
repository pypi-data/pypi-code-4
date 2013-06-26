from unittest import TestCase

from nose.case import FunctionTestCase
from nose.case import MethodTestCase
from nose.case import Test

from noselongdescription import LongDescriptionPlugin

def function():
    "This is a fake test function"

class FakeCase(object):
    "This is a fake test case"
    
    def method(self):
        "This is a fake test method"

class FakeUnittestCase(TestCase):
    __test__ = False
    
    def method(self):
        "This is a fake unittest test case method"

class TestPlugin(object):
    
    def _makeOne(self):
        return LongDescriptionPlugin()
    
    def test_name(self):
        "The plugin should be named 'long-description'"
        plugin = self._makeOne()
        assert 'long-description' == plugin.name
    
    def test_description_for_test_function(self):
        "The plugin should return a test function's description"
        plugin = self._makeOne()
        test = FunctionTestCase(function)
        description = plugin.describeTest(test)
        
        expected = "\n".join(["noselongdescription.tests.test_plugin:function",
                              '"""This is a fake test function"""'])
        assert description == expected, description
    
    def test_description_for_test_method(self):
        "The plugin should return a test method's description"
        plugin = self._makeOne()
        test = MethodTestCase(FakeCase.method)
        description = plugin.describeTest(test)
        
        expected = "\n".join(["noselongdescription.tests.test_plugin:FakeCase.method",
                              '"""This is a fake test method"""'])
        assert description == expected, description
    
    def test_description_for_unittest_case_method(self):
        "The plugin should return a unittest test method's description"
        plugin = self._makeOne()
        test = Test(FakeUnittestCase(methodName='method'))
        description = plugin.describeTest(test)
        
        expected = "\n".join(["noselongdescription.tests.test_plugin:FakeUnittestCase.method",
                              '"""This is a fake unittest test case method"""'])
        assert description == expected, description
