import sys

from nose2 import events
from nose2.util import _WritelnDecorator
import pygments
from pygments import lexers, formatters


class TracebackPrettyPrinter(_WritelnDecorator):
    def __init__(self, stream, pretty_print_traceback, ansi256):
        super(TracebackPrettyPrinter, self).__init__(stream)
        self.pretty_print_traceback = pretty_print_traceback
        self.ansi256 = ansi256

    def write(self, arg):
        if 'Traceback (most recent call last):' in arg and self.pretty_print_traceback:
            super(TracebackPrettyPrinter, self).write(self._prettyprint_traceback(arg))
        else:
            super(TracebackPrettyPrinter, self).write(arg)

    def writeln(self, arg=None):
        if arg and 'Traceback (most recent call last):' in arg and self.pretty_print_traceback:
            super(TracebackPrettyPrinter, self).writeln(self._prettyprint_traceback(arg))
        else:
            super(TracebackPrettyPrinter, self).writeln(arg)

    def _prettyprint_traceback(self, traceback):
        lexer = 'py3tb' if sys.version_info[0] == 3 else 'pytb'
        formatter = 'terminal%s' % '256' if self.ansi256 else ''
        return pygments.highlight(traceback, lexers.get_lexer_by_name(lexer),
                                  formatters.get_formatter_by_name(formatter))


class PrettyTracebackReporter(events.Plugin):
    commandLineSwitch = (
        None, 'pretty-print-traceback', 'Prettyprint Traceback on errors and failures')
    configSection = 'pretty-print'
    alwaysOn = True

    def __init__(self):
        self.pretty_print_traceback = self.config.as_bool('pretty_print_traceback', True)
        self.ansi256 = self.config.as_bool('ansi256', True)

    def beforeErrorList(self, event):
        event.stream = TracebackPrettyPrinter(event.stream, self.pretty_print_traceback, self.ansi256)
