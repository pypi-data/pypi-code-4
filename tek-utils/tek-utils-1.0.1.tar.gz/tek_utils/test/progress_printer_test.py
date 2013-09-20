import spec
import sure
from flexmock import flexmock

from tek import Configurations, logger

from tek_utils.sharehoster.common import ProgressPrinter


class ProgressPrinterTest(spec.Spec, ):

    class _Terminal(object):

        def __init__(self):
            self.log = []

        def pop(self):
            pass

        def push(self, msg):
            self.log.append(msg)

        def flush(self):
            pass

    def setup(self, *a, **kw):
        pass

    def output(self):
        terminal = self._Terminal()
        printer = ProgressPrinter(file_size=1000, _terminal=terminal)
        printer._init()
        printer.add(500)
        printer._step()
        printer.add(300)
        printer._step()
        printer.add(300)
        printer._step()
        expected = [' 50.00% ||   500.0 B of 1000.0 B  || at     0.00 B/s',
                    ' 80.00% ||   800.0 B of 1000.0 B  || at     0.00 B/s',
                    '110.00% ||    1.1 KB of 1000.0 B  || at     0.00 B/s']
        terminal.log.should.be(expected)

    def testfoo(self):
        try:
            raise Exception('asdfjkadf')
        except Exception as e:
            import sys
            import traceback
            traceback.print_exc()

__all__ = ['ProgressPrinterTest']
