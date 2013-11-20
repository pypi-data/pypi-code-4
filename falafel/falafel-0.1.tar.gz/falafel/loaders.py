import unittest

from .utils import iterate_tests


class FalafelTestLoader(unittest.TestLoader):

    def __init__(self, allowed_tests=None):
        super(FalafelTestLoader, self).__init__()
        self.allowed_tests = [] if allowed_tests is None else allowed_tests

    def getTestCaseNames(self, testCaseClass):
        # legacy code
        if hasattr(testCaseClass, 'createTests'):
            testCaseClass.createTests()

        if hasattr(testCaseClass, 'create_tests'):
            testCaseClass.create_tests()
        return super(FalafelTestLoader, self).getTestCaseNames(testCaseClass)

    def discover(self, *args, **kwargs):
        suite = super(FalafelTestLoader, self).discover(*args, **kwargs)

        # sort the suite
        if len(self.allowed_tests):
            tcases = list(iterate_tests(suite))
            newtfuncs = []
            for testclass in self.allowed_tests:
                testmethod = None
                if '.' in testclass:
                    testclass, testmethod = testclass.split('.')

                if not [x for x in tcases if testclass in
                        x.__class__.__name__]:
                    raise ValueError("unknown testclass '%s'. probably a typo ?" %
                                     testclass)
                if testmethod is not None:
                    if not [x for x in tcases if
                            testclass == x.__class__.__name__ and
                            testmethod in x._testMethodName]:
                        raise ValueError("unknown testmethod '%s' of testclass "
                                         "'%s'. probably a typo ?" %
                                         (testmethod, testclass))

                newtfuncs.append(unittest.TestSuite(
                    [x for x in iterate_tests(suite) if
                     x.__class__.__name__ == testclass and
                     (testmethod is None or testmethod == x._testMethodName)]))
            suite = unittest.TestSuite(newtfuncs)
        else:
            suite = unittest.TestSuite(
                sorted(iterate_tests(suite), key=lambda x: x.__class__.__name__))
        return suite
