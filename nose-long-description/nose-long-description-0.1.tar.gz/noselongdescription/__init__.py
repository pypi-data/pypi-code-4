from nose.plugins import Plugin

class LongDescriptionPlugin(Plugin):
    "A nose plugin that describes a test using both it's name and docstring"
    
    name = 'long-description'
    
    def describeTest(self, test):
        description = ":".join(test.address()[1:])
        
        actual_test = test
        while hasattr(actual_test, 'test'):
            actual_test = actual_test.test
        if actual_test.__doc__:
            description = "{0}\n\"\"\"{1}\"\"\"".format(description, actual_test.__doc__)
        return description

