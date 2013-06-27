from nose2 import events
from nose2.util import _WritelnDecorator
from colorama import Fore, Style, Back


class OutcomesPrettyPrinter(_WritelnDecorator):
    def __init__(self, stream, pretty_print_outcomes, short_label, long_label, foreground_color, background_color,
                 bold=False):
        super(OutcomesPrettyPrinter, self).__init__(stream)
        self.pretty_print_outcomes = pretty_print_outcomes
        self.short_label = short_label
        self.long_label = long_label
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.bold = bold

    def write(self, arg):
        super(OutcomesPrettyPrinter, self).write(self._prettyprint_outcomes(arg))

    def writeln(self, arg=None):
        super(OutcomesPrettyPrinter, self).writeln(self._prettyprint_outcomes(arg))

    def _prettyprint_outcomes(self, arg=None):
        if self.pretty_print_outcomes:
            if arg == self.short_label or arg == self.long_label:
                outcome = self.foreground_color + arg + Style.RESET_ALL

                if self.bold:
                    outcome = Style.BRIGHT + outcome

                return outcome

            elif self.long_label in arg:
                foreground_color = Fore.WHITE if self.background_color != Back.WHITE else Back.BLACK
                outcome = self.background_color + foreground_color + arg + Style.RESET_ALL

                if self.bold:
                    outcome = Style.BRIGHT + outcome

                return outcome
            else:
                return arg
        else:
            return arg


class PrettyOutcomesReporter(events.Plugin):
    commandLineSwitch = (
        None, 'pretty-print-outcomes', 'Prettyprint Traceback on errors and failures')
    configSection = 'pretty-print'
    alwaysOn = True

    def __init__(self):
        self.pretty_print_outcomes = self.config.as_bool('pretty_print_outcomes', True)

    def reportError(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'E', 'ERROR', Fore.RED, Back.RED,
                                             bold=True)

    def beforeErrorList(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'F', 'FAIL', Fore.RED, Back.RED,
                                             bold=True)
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'E', 'ERROR', Fore.RED, Back.RED,
                                             bold=True)
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, '.', 'OK', Fore.GREEN,
                                             Back.GREEN)

    def reportFailure(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'F', 'FAIL', Fore.RED, Back.RED,
                                             bold=True)

    def reportSkip(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 's',
                                             'skipped %s' % event.testEvent.reason,
                                             Fore.YELLOW, Back.YELLOW)

    def reportExpectedFailure(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'x', 'expected failure',
                                             Fore.MAGENTA, Back.MAGENTA)

    def reportUnexpectedSuccess(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, 'u', 'unexpected success',
                                             Fore.CYAN, Back.CYAN)

    def reportOtherOutcome(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, '?', 'unknown outcome',
                                             Fore.BLUE, Back.BLUE)

    def reportSuccess(self, event):
        event.stream = OutcomesPrettyPrinter(event.stream, self.pretty_print_outcomes, '.', 'ok', Fore.GREEN,
                                             Back.GREEN, bold=True)