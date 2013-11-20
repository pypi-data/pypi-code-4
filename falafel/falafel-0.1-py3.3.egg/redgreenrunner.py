"""colorized unittest output

taken from https://github.com/stevematney/redgreenunittests
"""

import sys

from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import TerminalFormatter

import unittest

OKGREEN = '\033[92m'
SKIP = '\033[93m'
WARNING = '\033[94m'
FAIL = '\033[91m'
ENDC = '\033[0m'


class _RedGreenWritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def _writehelper(self, text, color, newline=False):
        newtext = "%s%s%s" % (color, text, ENDC)
        self.stream.write(newtext)
        if newline:
            self.stream.write('\n')
        self.stream.flush()

    def writeln(self, *args):
        if len(args) == 1:
            self.stream.write(args[0])
            self.stream.write('\n')
        elif len(args) == 2:
            text = args[0]
            color = args[1]
            self._writehelper(text, color, newline=True)

    def write(self, *args):
        if len(args) == 1:
            # with these two checks we don't need to overload the run method
            # of TextTestRunner
            if args[0] == 'OK':
                self._writehelper(args[0], OKGREEN)
            elif args[0] == 'FAILURE':
                self._writehelper(args[0], FAIL)
            else:
                self.stream.write(args[0])
        elif len(args) == 2:
            text = args[0]
            color = args[1]
            self._writehelper(text, color)


class RedGreenTextTestResult(unittest.TextTestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def addSuccess(self, test):
        super(unittest.TextTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.writeln("ok", OKGREEN)
        elif self.dots:
            self.stream.write('.', OKGREEN)

    def addError(self, test, err):
        super(unittest.TextTestResult, self).addError(test, err)
        if self.showAll:
            self.stream.writeln("ERROR", WARNING)
        elif self.dots:
            self.stream.write('E', WARNING)

    def addSkip(self, test, reason):
        super(unittest.TextTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.writeln("skipped {0!r}".format(reason), SKIP)
        elif self.dots:
            self.stream.write("s", SKIP)
            self.stream.flush()

    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        self.stream.write(FAIL)
        if self.showAll:
            pass
            # self.stream.writeln("FAIL", FAIL)
        elif self.dots:
            self.stream.write('F', FAIL)

    def addExpectedFailure(self, test, err):
        super(unittest.TextTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.writeln("expected failure", OKGREEN)
        elif self.dots:
            self.stream.write("x", OKGREEN)

    def addUnexpectedSuccess(self, test):
        super(unittest.TextTestResult, self).addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.writeln("unexpected success", FAIL)
        elif self.dots:
            self.stream.write("u", FAIL)

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors, WARNING)
        self.printErrorList('FAIL', self.failures, FAIL)

    def printErrorList(self, flavour, errors, color):
        for test, err in errors:
            self.stream.write(color)
            self.stream.writeln("%s" % err)

    def _exc_info_to_string(self, err, test):
        code = super(RedGreenTextTestResult,
                     self)._exc_info_to_string(err, test)
        return highlight(code, PythonTracebackLexer(), TerminalFormatter())[:-1]


class RedGreenTextTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = RedGreenTextTestResult

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None,
                 width=None, pdb=False, warnings=None):
        self.stream = _RedGreenWritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass
        if width is not None:
            self.resultclass.width = width
            self.resultclass.separator1 = '=' * width
            self.resultclass.separator2 = '-' * width
        self.resultclass.ipdb = pdb
