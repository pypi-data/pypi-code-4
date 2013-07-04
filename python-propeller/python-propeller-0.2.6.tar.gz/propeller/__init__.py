# -*- coding: utf8 -*-
from __future__ import print_function
__author__ = 'mb@nexttuesday.de'
"""

 )¯¯`'¯¸¯¯`,)¯¯|)¯¯)'‚/¯¯|\¯¯¯\')¯¯`'¯¸¯¯`,   ___   )¯¯ )'     )¯¯ )'         ___   )¯¯|)¯¯)'‚
(____)–-·´'(__(\ ¯¯¯(°\__'\|__/(____)–-·´'|¯¯(\__('(___(¸.––-,(___(¸.––-,°|¯¯(\__('(__(\ ¯¯¯(°
       °        ¯¯¯¯                    ° |__(/¯¯¯(‘      ¯¯¯        ¯¯¯  |__(/¯¯¯(‘     ¯¯¯¯
              '‚                        '‚    ¯¯¯¯'‘                          ¯¯¯¯'‘

Copyright (c) 2013, Thomas Einsporn, Manuel Barkhau
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the python-propeller nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
from locale import getpreferredencoding
from time import time
from threading import Thread, Event
from util import term_size


SPINNERS = {
    'shades': u" ┄░▒▓█▓▒░┄",
    'hbar': u" ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",
    'vbar': u" ▏▎▍▌▋▊▉█▉▊▌▍▎▏",
    'dots': u"⠀⠁⠃⠇⡇⣇⣧⣷⣿⣾⣼⣸⢸⠸⠘⠈",
    'lines': u"|/-\\",
    'striped_box': u"□▤▥▧▨▦▩■▩▦▨▧▥▤",
    'circle_halfs': u"◐◓◑◒",
    'corners': u"⌜⌝⌟⌞",
    '34_corners': u"▜▟▙▛",
    'box_corners': u"▖▘▝▗",
    'circle_corners': u"◜◝◞◟",
    'triangle_corners': u"◸◹◿◺",
    'full_triangle_corners': u"◣◤◥◢",
    'box_corners': u"◳◲◱◰",
    '14circle_corners': u"◴◷◶◵"
}

BARS = {
    'shades': u" ┄░▒▓█",
    'hbar': u" ▁▂▃▄▅▆▇█",
    'vbar': u" ▏▎▍▌▋▊▉█",
    'dots': u"⠀⠁⠃⠇⡇⣇⣧⣷⣿",
    'lines': u" -+=",
    '4box': u" ▖▌▛█",
    'striped_box': u" ▥▧▦▩▣",
}

# TODO: implement
BOUNCERS = {
    
}

def print_styles():
    print("spinner styles:")
    for s in SPINNERS.items():
        print(u"% 22s: %s" % s)

    print("progress bar styles:")
    for b in BARS.items():
        print(u"% 22s: %s" % b)


MIN = 60.0
HOUR = MIN * 60.0
DAY = HOUR * 24.0


class propeller(object):

    def __init__(self, msg="", ops=True, eta=True, percent=True,
                 spinner='shades', bar='shades'):

        self._msg = msg or ""
        self._eta = eta
        self._percent = percent
        self._ops = ops

        self._spinner = SPINNERS.get(spinner, spinner)
        self._bar = BARS.get(bar, bar)
        # position in spinner
        self._pos = None

        if sys.stdout.isatty():
            self._terminal = True
            self._encoding = sys.stdout.encoding
        else:
            self._terminal = False
            self._encoding = getpreferredencoding()

        self._i = None
        self._n = None

        self._t_start = None
        self._t_cur = None
        self._t_last = None
        self._t_avg = 0
        self._ops_done = 0

        self._cols = 0

        self._update_stop = Event()
        self._update_thread = Thread(target=self._update_loop)
        self._update_thread.start()

    def _update_loop(self):
        self._update_stop.wait(.1)  # initial wait for user code

        while not self._update_stop.isSet():
            if self._t_cur is self._t_last and self._t_cur is not None:
                pass    # nothing to do
            elif self._i is not None:
                self._write_bar()
            else:
                if self._pos is None:
                    self._pos = 0
                self._write_spinner()
                self._pos += 1

            self._t_last = self._t_cur
            self._update_stop.wait(.3)

    def _write_bar(self):
        self._clearln()
        barlen = self._cols - len(self._msg)

        ops = self._ops_str() if self._ops else ""
        barlen -= len(ops)

        eta = self._eta_str() if self._eta else ""
        barlen -= len(eta)

        percent = self._percent_str() if self._percent else ""
        barlen -= len(percent)

        if self._msg:
            sys.stdout.write(self._msg)

        sys.stdout.write(self._bar_str(barlen))
        if ops:
            sys.stdout.write(ops)
        if eta:
            sys.stdout.write(eta)
        if percent:
            sys.stdout.write(percent)
        sys.stdout.flush()

    def _write_spinner(self):
        self._clearln()

        ops = self._ops_str() if self._ops else ""
        spin = self._spin_str()
        padding = self._cols - (len(spin) + len(self._msg) + len(ops))

        sys.stdout.write(self._msg)
        sys.stdout.write(spin)
        sys.stdout.write(padding * " ")
        sys.stdout.write(ops)
        sys.stdout.flush()

    def _clearln(self):
        sys.stdout.write("\b" * self._cols)
        rows, cols = term_size()
        self._cols = cols

    def _eta_str(self):
        if not (self._i and self._n and self._t_start):
            return "[eta:???]"

        elapsed = time() - self._t_start
        left = (self._n - self._i) * (elapsed / self._i)

        if left < 100:
            return "[eta:% 3ds]" % left
        if left < 100 * MIN:
            return "[eta:% 3dm]" % (left / MIN)
        if left < 100 * HOUR:
            return "[eta:%3.1fh]" % (left / HOUR)
        return "[eta:%3.1fd]" % (left / DAY)

    def _percent_str(self):
        if self._i is None or self._n is None:
            return "[ ??%]"
        return "[%3d%%]" % (round(self._i * 100.0) / self._n)

    def _ops_str(self):
        if not (self._t_start and self._t_avg > 0):
            return "[ops: ???]"

        ops = 1 / self._t_avg
        if ops < 20:
            return "[ops:%4.1f]" % ops
        return "[ops:% 4d]" % ops

    def _spin_str(self):
        return "[" + self._spinner[self._pos % len(self._spinner)] + "]"

    def _bar_str(self, barlen):
        null_chr = self._bar[0]
        full_chr = self._bar[-1]

        if not (self._i and self._n):
            return null_chr * barlen

        barlen = max(1, barlen)
        sub_len = len(self._bar)

        i_elapsed = float(self._i) / float(self._n)
        elapsed = int(barlen * i_elapsed)
        pos = int((i_elapsed * barlen * sub_len) % sub_len)
        rest = (barlen - elapsed) - 1
        pos_str = self._bar[pos] if rest > 0 else ""
        return elapsed * full_chr + pos_str + rest * null_chr

    def _t_update(self):
        if self._t_start is None:
            self._t_start = time()

        if self._t_cur:
            dt = time() - self._t_cur
            if self._t_avg is None:
                self._t_avg = dt
            elif dt < .01:
                self._t_avg = (self._t_avg * 98 + dt) / 99
            elif dt < .1:
                self._t_avg = (self._t_avg * 8 + dt) / 9
            elif dt < .5:
                self._t_avg = (self._t_avg * 2 + dt) / 3
            elif dt < 1:
                self._t_avg = (self._t_avg + dt) / 2
            else:
                self._t_avg = (self._t_avg + dt * 2) / 3

        self._t_cur = time()

    def progress(self, i, n):
        self._t_update()

        self._n = n
        self._i = i

    def spin(self):
        self._t_update()

    def end(self, s=None):
        if s:
            self.msg(s)

        if self._update_stop.isSet():
            return

        self._update_stop.set()
        if self._i is not None:
            # last update of progress bar to show as completed
            self._i = self._n
            self._write_bar()

        sys.stdout.write("\n")
        sys.stdout.flush()

    def println(self, s):
        self._clearln()
        sys.stdout.write(s)
        sys.stdout.write((self._cols - len(s)) * " ")
        sys.stdout.write("\n")
        sys.stdout.flush()

    def msg(self, msg):
        self._msg = msg

    # convenience methods for collection processing

    def imap(self, function, *sequences, **kwargs):
        try:
            self.spin()

            if 'n' in kwargs:
                total_len = kwargs['n']
            else:
                total_len = 0
                for sequence in sequences:
                    if hasattr(sequence, '__len__'):
                        total_len += len(sequence)
                    else:
                        total_len = None
                        break

            i = 0
            for sequence in sequences:
                for item in sequence:
                    if total_len is None:
                        self.spin()
                    else:
                        self.progress(i, total_len)

                    yield function(item)
                    i += 1
        finally:
            self.end()

    def process(self, function, *sequences, **kwargs):
        for _ in self.imap(function, *sequences, **kwargs):
            pass

    def map(self, function, *sequences, **kwargs):
        return list(self.imap(function, *sequences, **kwargs))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.end()


def demo(argv=None):
    def noop(item):
        from time import sleep
        sleep(0.01)

    def work(n=600):
        return iter(xrange(n))

    propeller("lines spinner ", spinner='lines').process(noop, work())
    propeller("shade spinner ", spinner='shades').process(noop, work())
    propeller("vbar spinner ", spinner='vbar').process(noop, work())
    propeller("hbar spinner ", spinner='hbar').process(noop, work())
    propeller("dots spinner ", spinner='dots').process(noop, work())

    n = 10000  # simulate longer loading so intermediate steps are visible
    propeller("lines progress bar ", bar='lines').process(noop, work(), n=n)
    propeller("shade progress bar ", bar='shades').process(noop, work(), n=n)
    propeller("vbar progress bar ", bar='vbar').process(noop, work(), n=n)
    propeller("hbar progress bar ", bar='hbar').process(noop, work(), n=n)
    propeller("dots progress bar ", bar='dots').process(noop, work(), n=n)

    return 0

if __name__ == "__main__":
    sys.exit(demo(sys.argv))
