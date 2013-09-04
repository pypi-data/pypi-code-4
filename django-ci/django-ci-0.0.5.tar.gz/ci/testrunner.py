from django_test_exclude.runners import ExcludeTestSuiteRunner
from django.utils.unittest.runner import TextTestRunner, TextTestResult
from unittest.util import strclass
import traceback
import json


class JSONTestResult(TextTestResult):

    def addSuccess(self, test):
        super(JSONTestResult, self).addSuccess(test)
        self.addResult(test, status="success")

    def addError(self, test, err):
        super(JSONTestResult, self).addError(test, err)
        self.addResult(test, status="error", error=err)

    def addFailure(self, test, err):
        super(JSONTestResult, self).addFailure(test, err)
        self.addResult(test, status="fail", error=err)

    def addSkip(self, test, reason):
        super(JSONTestResult, self).addSkip(test, reason)
        self.addResult(test, status="skip", error=reason)

    def addExpectedFailure(self, test, err):
        super(JSONTestResult, self).addExpectedFailure(test, err)
        self.addResult(test, status="expected failure", error=err)

    def addUnexpectedSuccess(self, test):
        super(JSONTestResult, self).addUnexpectedSuccess(test)
        self.addResult(test, status="unexpected success")

    def addResult(self, test, status, error=None):
        if not hasattr(test, "_testMethodName"):
            print test, status, dir(test)
            print error
        else:
            data = dict(
                name="%s" % test._testMethodName,
                status=status,
            )
            desc = test.shortDescription()
            if desc:
                data["description"] = desc
            if error:
                if isinstance(error, basestring):
                    data["error"] = error
                else:
                    data["error"] = "".join(traceback.format_exception(*error))

            module = strclass(test.__class__)
            tests = self.results.get(module, [])
            tests.append(data)
            self.results[module] = tests

    def startTestRun(self):
        super(JSONTestResult, self).startTestRun()
        self.results = {}

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)


class JSONTestRunner(TextTestRunner):
    resultclass = JSONTestResult


class TestSuiteRunner(ExcludeTestSuiteRunner):

    def run_suite(self, suite, **kwargs):

        self.retval = JSONTestRunner(
            verbosity=self.verbosity, failfast=self.failfast).run(suite)

        return self.retval

    def run_tests(self, test_labels, extra_tests=None, **kwargs):

#         import danemco.utils.traceprints

        test_results = super(TestSuiteRunner, self).run_tests(test_labels, extra_tests, **kwargs)

        fileh = open("testresults.json", "w")
        fileh.write(json.dumps(self.retval.results))
        fileh.close()
        return test_results


