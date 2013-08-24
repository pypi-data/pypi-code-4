#!/usr/bin/python
#coding: utf-8
"""A nose plugin: Just make the python standard module: nose output with formatted and colorful more like XUnit output.
"""

import os
import sys
import time
import traceback
from nose.plugins import Plugin
from nose.core import TextTestRunner
try:
    from colorama import init, Fore, AnsiToWin32
except:
    raise ImportError, "colorama isn't installed"

class MColorStreamCrossPlatform(object):
    """decorate the stream: add some useful methods"""
    def __init__(self, stream=sys.stderr):
        # init the colorama
        init()
        self.fore = Fore
        if os.name == 'nt':
            #on windows, show color instead of ASCII sequences.
            self.stream = AnsiToWin32(sys.stderr).stream 
        else:
            self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AtrributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, msg=None):
        if msg:
            self.write(msg)
        self.write('\n')

    def red(self, msg):
        self.write(self.fore.RED + msg + self.fore.RESET)

    def green(self, msg):
        self.write(self.fore.GREEN + msg + self.fore.RESET)

    def yellow(self, msg):
        self.write(self.fore.YELLOW + msg + self.fore.RESET)

    def cyan(self, msg):
        self.write(self.fore.CYAN + msg + self.fore.RESET)

    def white(self, msg):
        self.write(self.fore.WHITE + msg + self.fore.RESET)

    def blue(self, msg):
        self.write(self.fore.BLUE + msg + self.fore.RESET)

    def magenta(self, msg):
        self.write(self.fore.MAGENTA + msg + self.fore.RESET)


class MTextTestRunner(TextTestRunner):
    """Just only show our own output: 
        1). The key is to comment the result.printErrors()
        2). Used by ColorUnit:prepareTestRunner()"""
    def __init__(self, stream):
        super(MTextTestRunner, self).__init__()

    def run(self, test):
        result = self._makeResult()
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        #result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result


class ColorUnit(Plugin):
    """print the output with formated and colorful, just more like xunit."""
    name = "colorunit"
    score = 20
    encoding = "UTF-8"

    def __init__(self):
        super(ColorUnit, self).__init__() # involved the Plugin init
        self.stream = MColorStreamCrossPlatform(sys.stderr)
        self.separator1 = "=" * 70
        self.separator2 = "-" * 70
        self.STDOUT_LINE = '\nStdout:\n%s'
        self.STDERR_LINE = '\nStderr:\n%s'
        self.showAll = False
        self.buffer = False
        self.dots = True
        self.descriptions = True

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return "\n".join((str(test)), doc_first_line)
        else:
            return str(test)

    def startTest(self, test):
        self.stream.writeln(self.separator1)
        self.stream.cyan("[RUN\t]")
        self.stream.writeln(self.getDescription(test))
        if self.showAll:
            self.stream.writeln(self.getDescription(test))
            self.stream.writeln(" ... ")
            self.stream.flush()
        self.startTime = self.timer()

    def stopTest(self, test):
        self.stream.writeln()
    
    def addSuccess(self, test):
        self.taken_time = self.timer(self.startTime)
        if self.showAll:
            self.stream.writeln("ok")
        elif self.dots:
            self.stream.green('[OK\t]')
            self.stream.write(self.getDescription(test))
            self.stream.writeln("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.stream.flush()

    def addError(self, test, err):
        self.taken_time = self.timer(self.startTime)
        if self.showAll:
            self.stream.writeln("ERROR")
        elif self.dots:
            self.stream.yellow('[ERROR\t]')
            self.stream.write(self.getDescription(test))
            self.stream.writeln("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.show_beautiful_exc_info(self._exc_info_to_string(err, test))
            self.stream.flush()

    def addFailure(self, test, err):
        self.taken_time = self.timer(self.startTime)
        if self.showAll:
            self.stream.writeln("FAIL")
        elif self.dots:
            self.stream.red('[FAIL\t]')
            self.stream.write(self.getDescription(test))
            self.stream.writeln("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.show_beautiful_exc_info(self._exc_info_to_string(err, test))
            self.stream.flush()

    def addSkip(self, test, reason):
        self.taken_time = self.timer(self.startTime)
        if self.showAll:
            self.stream.writeln("SKIP")
        elif self.dots:
            self.stream.blue("[SKIP\t]")
            self.stream.write(self.getDescription(test))
            self.stream.writeln("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.stream.writeln("{0}".format(reason))
            self.stream.flush()

    def printErrors(self):
        pass

    def printErrorList(self, flavour, errors):
        pass


    def finalize(self, result):
        pass
    
    def prepareTestRunner(self, runner):
        self.runner = MTextTestRunner(self.stream)
        return self.runner

    def setOutputStream(self, stream):
        return self.stream

    def show_beautiful_exc_info(self, exc_info_string):
        """make the key message of exc_info outstand, It's easily and quickly to find the evil"""
        if exc_info_string.endswith("\n"):
            exc_info_string = exc_info_string[:-1] #trim the last '\n'
        describleMsg, linefeed, keyMsg = exc_info_string.rpartition("\n")
        self.stream.writeln(describleMsg)
        self.stream.magenta(keyMsg)
        self.stream.writeln()

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(self.STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(self.STDERR_LINE % error)
        return ''.join(msgLines)

    def timer(self, otherTime=0):
        if os.name == "nt":
            begin_point = time.clock()
        else:
            begin_point = time.time()
        return begin_point - otherTime

    def _is_relevant_tb_level(self, tb):
        return '__unittest' in tb.tb_frame.f_globals


    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length
