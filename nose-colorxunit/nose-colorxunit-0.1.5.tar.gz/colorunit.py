#!/usr/bin/python
#coding: utf-8
#author: Lesus <walkingnine@gmail.com>
"""A nose plugin: Just make the python standard module: 
nose output with formatted and colorful more like XUnit output.
"""

import os
import io
import sys
import time
import traceback
import ConfigParser as CP
from nose.plugins import Plugin
from nose.core import TextTestRunner
try:
    from colorama import init, Fore, Back, Style, AnsiToWin32
except:
    raise ImportError, "colorama isn't installed"


class ConfReader(object):
    """read the configurational file. Used by MColorStreamCrossPlatform"""
    default_colormap = """
[Fore]
Run = cyan
OK= green
Error= yellow
Fail= red
Skip= blue
KeyMsg= magenta
Time= white

[Style]
Style= bright

[Back]
Run = ""
OK = ""
Error  = ""
Fail = ""
Skip = ""
KeyMsg = ""
Time = ""
"""
    def __init__(self, conf_file="colorunit_conf.ini"):
        self.conf_file = conf_file.lower()
        if os.path.exists(self.conf_file):
            self.config = CP.ConfigParser()
            self.config.read(self.conf_file)
        else:
            self.config = CP.RawConfigParser(allow_no_value=True)
            self.config.readfp(io.BytesIO(ConfReader.default_colormap))
        self.fore = Fore
        self.back = Back
        self.style = Style

    def configSectionMap(self, section):
        """Get the section in the configurational file
        1) section is one of Fore, Back or Style"""
        self.config_map = {}
        self.system_map = {}
        if section == "Fore":
            self.system_map = {'green': self.fore.GREEN,'blue': self.fore.BLUE, 
                        'white': self.fore.WHITE, 'magenta': self.fore.MAGENTA, 
                        'yellow': self.fore.YELLOW,    'red': self.fore.RED, 
                        'cyan': self.fore.CYAN}
        elif section == "Back":
            self.system_map = {'green': self.back.GREEN,'blue': self.back.BLUE, 
                        'white': self.back.WHITE, 'magenta': self.back.MAGENTA, 
                        'yellow': self.back.YELLOW,    'red': self.back.RED, 
                        'cyan': self.back.CYAN}
        elif section == "Style":
            self.system_map = {'normal': self.style.NORMAL, 
                    'bright': self.style.BRIGHT, 'dim': self.style.DIM}
            
        options = self.config.options(section)
        for option in options:
            self.config_map[option] = self.config.get(section, option)

    def getValue(self, section, key):
        """According to section and key, return the value.
        for example: 
        if:   section = 'Fore', key='error' 
        then: self.config_map={'error':"red"}
              self.system_map = {'red': self.fore.RED}
        return self.system_map[self.config_map['error']]
        """
        self.configSectionMap(section)
        if not self.config_map.has_key(key):
            raise KeyError, "Please check the key in the " + self.conf_file \
                    + " file if it exists spelling error"
        system_map_key = self.config_map.get(key)
        if self.system_map.has_key(system_map_key) or system_map_key == "": 
            #if system_map has key or system_map_key is "", 
            #then return the right value, 
            if self.system_map.has_key(system_map_key):
                system_map_value = self.system_map.get(system_map_key)
            else:
                system_map_value = ""
        else:
            raise KeyError, "Please check the value in the " + self.conf_file \
                    + " file if it exists spelling error"

        return system_map_value

    def showColorMsg(self, key, msg):
        return self.getValue("Fore", key) + self.getValue("Back", key) + \
                self.getValue("Style", "style") + msg + self.style.RESET_ALL


class MColorStreamCrossPlatform(object):
    """decorate the stream: add some useful methods"""
    def __init__(self, stream=sys.stderr, conf_file="colorunit_conf.ini"):
        # init the colorama
        init()
        self.confReader = ConfReader(conf_file)
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

    def run(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("run", msg))
        if linefeed:
            self.writeln()

    def ok(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("ok", msg))
        if linefeed:
            self.writeln()

    def error(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("error", msg))
        if linefeed:
            self.writeln()

    def fail(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("fail", msg))
        if linefeed:
            self.writeln()

    def skip(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("skip", msg))
        if linefeed:
            self.writeln()

    def keyMsg(self, msg, linefeed=False):
        self.write(self.confReader.showColorMsg("keymsg", msg))
        if linefeed:
            self.writeln()

    def showTime(self, msg, linefeed=True):
        self.write(self.confReader.showColorMsg("time", msg))
        if linefeed:
            self.writeln()


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
        self.startTimer = 0

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return "\n".join((str(test)), doc_first_line)
        else:
            return str(test)

    def startTest(self, test):
        self.stream.writeln(self.separator1)
        self.stream.run("[RUN\t]")
        self.stream.writeln(self.getDescription(test))
        if self.showAll:
            self.stream.writeln(self.getDescription(test))
            self.stream.writeln(" ... ")
            self.stream.flush()
        self.startTimer = self.timer()

    def stopTest(self, test):
        self.stream.writeln()
    
    def addSuccess(self, test):
        self.taken_time = self.timer(self.startTimer)
        if self.showAll:
            self.stream.ok("ok")
        elif self.dots:
            self.stream.ok('[OK\t]')
            self.stream.write(self.getDescription(test))
            self.stream.showTime("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.stream.flush()

    def addError(self, test, err):
        self.taken_time = self.timer(self.startTimer)
        if self.showAll:
            self.stream.error("ERROR")
        elif self.dots:
            self.stream.error('[ERROR\t]')
            self.stream.write(self.getDescription(test))
            self.stream.showTime("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.show_beautiful_exc_info(self._exc_info_to_string(err, test))
            self.stream.flush()

    def addFailure(self, test, err):
        self.taken_time = self.timer(self.startTimer)
        if self.showAll:
            self.stream.fail("FAIL")
        elif self.dots:
            self.stream.fail('[FAIL\t]')
            self.stream.write(self.getDescription(test))
            self.stream.showTime("  {0:.4f} sec".format(round(self.taken_time, 4)))
            self.show_beautiful_exc_info(self._exc_info_to_string(err, test))
            self.stream.flush()

    def addSkip(self, test, reason):
        self.taken_time = self.timer(self.startTimer)
        if self.showAll:
            self.stream.skip("SKIP")
        elif self.dots:
            self.stream.skip("[SKIP\t]")
            self.stream.write(self.getDescription(test))
            self.stream.showTime("  {0:.4f} sec".format(round(self.taken_time, 4)))
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
        """make the key message of exc_info outstand, 
        It's easily and quickly to find the evil"""
        if exc_info_string.endswith("\n"):
            exc_info_string = exc_info_string[:-1] #trim the last '\n'
        describleMsg, linefeed, keyMsg = exc_info_string.rpartition("\n")
        self.stream.writeln(describleMsg)
        self.stream.keyMsg(keyMsg)
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
        """calculate the taken time
        1) if otherTime equals 0, it will return now"""
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
