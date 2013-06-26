from nose.plugins import Plugin

class LongDescriptionPlugin(Plugin):
    "A nose plugin that describes a test using both it's name and docstring"
    
    name = 'long-description'
    
    def _get_docstring(self, test):
        if test.__doc__:
            return test.__doc__
        elif hasattr(test, '_testMethodDoc'):
            return test._testMethodDoc
    
    def describeTest(self, test):
        description = ":".join(test.address()[1:])
        
        actual_test = test
        while hasattr(actual_test, 'test'):
            actual_test = actual_test.test
        docstring = self._get_docstring(actual_test)
        if docstring:
            description = "{0}\n\"\"\"{1}\"\"\"".format(description, docstring)
        return description

