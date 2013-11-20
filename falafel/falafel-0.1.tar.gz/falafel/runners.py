import logging
import unittest
import os
import sys
import inspect
import re

if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


from .redgreenrunner import RedGreenTextTestResult
from .redgreenrunner import RedGreenTextTestRunner
from .redgreenrunner import WARNING
from .redgreenrunner import FAIL
from .logger import Formatter
from .logger import nocolors


class ResultStream(object):

    def __init__(self, orig_stream):
        self.orig_stream = orig_stream
        self.logfile = None
        self.logger = None  # is set in the TestRunner class
        self.onlylogtologfile = True
        self.ansi_escape = re.compile(r'\x1b[^m]*m')

    def flush(self):
        self.orig_stream.flush()
        if self.logfile:
            self.logfile.flush()

    def write(self, text):
        self.orig_stream.write(text)
        if self.logfile:
            self.logfile.write(self.ansi_escape.sub('', text))

    def open_file(self, fname, warnstream):
        self.logfile = open(fname, "w")
        if self.logger is None:
            return
        nocolfmt = Formatter(pre=nocolors, lenstrip=None, contline=None)
        if self.onlylogtologfile:
            hdl = logging.StreamHandler(self.logfile)
            fmt = nocolfmt
        else:
            hdl = logging.StreamHandler(self)
            fmt = Formatter()
        hdl.setFormatter(fmt)
        self.logger.addHandler(hdl)
        hdl = logging.StreamHandler(warnstream)
        hdl.setLevel(logging.WARNING)
        hdl.setFormatter(nocolfmt)
        self.logger.addHandler(hdl)

    def close_file(self):
        if self.logfile:
            self.logfile.close()
            self.logfile = None

            if self.logger is not None:
                self.logger.removeHandler(self.logger.handlers[0])
                self.logger.removeHandler(self.logger.handlers[0])


class ResultHandler(RedGreenTextTestResult):

    ipdb = False
    width = 80

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)  # increments the number of
                                                   # run tests counter

        tname = '%s.%s' % (test.__class__.__name__, test._testMethodName)
        module = test.__class__.__module__
        desc = ' %s in %s ' % (tname, module)
        logfile = os.path.join('log', '%s.log' % (tname.replace('.', '_')))
        test.warningserrors = StringIO()
        self.stream.open_file(logfile, test.warningserrors)
        self.stream.writeln(desc.center(self.width, '-'))
        self.stream.flush()

    def stopTest(self, test):
        if test.created_files:
            self.stream.writeln("Created files:")
            for fn in sorted(test.created_files):
                self.stream.writeln("\t%s" % fn)
        if test.data:
            self.stream.writeln("Created data:")
            for k, v in sorted(test.data.iteritems()):
                self.stream.writeln("%s:\t%s" % (k, v))

        warnings = test.warningserrors.getvalue()
        test.warningserrors.close()
        if len(warnings):
            self.stream.writeln("Errors and Warnings logged:", WARNING)
            s = warnings.split('\n')
            s = ['\t' + line for line in s]
            self.stream.writeln('\n'.join(s), WARNING)

        self.stream.writeln(self.separator2)
        self.stream.close_file()
        self.stream.writeln('')

    def addError(self, test, err):
        super(ResultHandler, self).addError(test, err)
        self.print_current_error()
        if self.ipdb:
            self.debug(err)

    def addFailure(self, test, err):
        super(ResultHandler, self).addFailure(test, err)
        self.print_current_failure()
        if self.ipdb:
            self.debug(err)

    def debug(self, err):
        import IPython
        ec, ev, tb = err
        stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            # The IPython API changed a bit so we should
            # support the new version
            if hasattr(IPython, 'InteractiveShell'):
                if hasattr(IPython.InteractiveShell, 'instance'):
                    shell = IPython.InteractiveShell.instance()
                    p = IPython.core.debugger.Pdb(shell.colors)
                else:
                    shell = IPython.InteractiveShell()
                    ip = IPython.core.ipapi.get()
                    p = IPython.core.debugger.Pdb(ip.colors)
            # and keep support for older versions
            else:
                shell = IPython.Shell.IPShell(argv=[''])
                ip = IPython.ipapi.get()
                p = IPython.Debugger.Pdb(ip.options.colors)

            p.reset()
            # inspect.trace() returns a list of frame information from this
            # frame to the one that raised the exception being treated
            frame, filename, line, func_name, ctx, idx = inspect.trace()[-1]
            p.interaction(frame, tb)
        finally:
            sys.stdout = stdout

    def print_current_error(self):
        cerr = self.errors[-1:]
        self.printErrorList('ERROR', cerr, WARNING)

    def print_current_failure(self):
        cfail = self.failures[-1:]
        self.printErrorList('FAIL', cfail, FAIL)

    def printErrors(self):
        # this prevents that all errors/failures a printed after all tests
        # were ran
        pass


class FalafelTestRunner(RedGreenTextTestRunner):

    def __init__(self, *args, **kwargs):
        kwargs["stream"] = ResultStream(sys.stderr)
        kwargs["resultclass"] = ResultHandler

        logger = kwargs.pop('logger', None)
        if logger is not None:
            kwargs['stream'].logger = logger
            if kwargs.pop('debug', False):
                kwargs['stream'].onlylogtologfile = False  # log to logfile
                                                           # as well to
                                                           # stdout

        super(FalafelTestRunner, self).__init__(*args, **kwargs)
