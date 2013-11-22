#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
from StringIO import StringIO


class TeeStream(StringIO):
    def __init__(self, terminal_type, capture):
        if terminal_type not in ['stdout', 'stderr']:
            raise Exception('Invalid terminal type')
        self.terminal_type = terminal_type
        self.terminal = sys.__dict__[self.terminal_type]
        self.capture = capture
        StringIO.__init__(self)

    def fileno(self):
        return sys.__dict__[self.terminal_type].fileno()

    def write(self, message):
        self.terminal.write(message)
        self.capture.write(message)


