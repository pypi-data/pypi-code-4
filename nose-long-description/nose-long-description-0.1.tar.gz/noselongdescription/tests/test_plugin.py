from nose.case import FunctionTestCase
from nose.case import MethodTestCase

from noselongdescription import LongDescriptionPlugin

def function():
    "This is a fake test function"

class FakeCase(object):
    "This is a fake test case"
    
    def method(self):
        "This is a fake test method"

class TestPlugin(object):
    
    def _makeOne(self):
        return LongDescriptionPlugin()
    
    def test_name(self):
        "The plugin should be named 'long-description'"
        plugin = self._makeOne()
        assert 'long-description' == plugin.name
    
    def test_description_for_test_function(self):
        "The plugin should report a test function's docstring"
        plugin = self._makeOne()
        test = FunctionTestCase(function)
        print dir(test)
        description = plugin.describeTest(test)
        
        expected = "\n".join(["noselongdescription.tests.test_plugin:function",
                              '"""This is a fake test function"""'])
        assert description == expected, description
    
    def test_description_for_test_method(self):
        "The plugin should report a test method's docstring"
        plugin = self._makeOne()
        test = MethodTestCase(FakeCase.method)
        print dir(test)
        description = plugin.describeTest(test)
        
        expected = "\n".join(["noselongdescription.tests.test_plugin:FakeCase.method",
                              '"""This is a fake test method"""'])
        assert description == expected, description
