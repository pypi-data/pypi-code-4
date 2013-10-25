# Copyright 2013 Sven Bartscher
#
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

#This file is part of cursgame 0.1.0

import time
from collections import defaultdict
import curses

def nothing(*args, **kwargs):
    pass

class InputHandler(object):
    def __init__(self, blocking):
        self.callbacks = defaultdict(lambda: nothing)
        self.blocking = blocking
        self._screen = None

    @property
    def screen(self):
        if not self._screen:
            raise RuntimeError("{0} isn't initialized!".format(self))
        return self._screen

    @screen.setter
    def screen(self, value):
        self._screen = value
        try:
            value.nodelay(bool(self.blocking))
        except NameError:
            raise TypeError("screen must be a valid screen object!")

    @screen.deleter
    def screen(self):
        self._screen = None

    def get_input(self):
        "Get input from screen and call callbacks"
        if self.blocking:
            time.sleep(self.blocking)
        try:
            inp = self.screen.getch()
        except curses.error:
            pass
        else:
            self.callbacks[inp](inp)

#Get all key constants from curses
do = globals()
dc = curses.__dict__
for symbol, value in dc.items():
    if symbol.startswith('KEY_'):
        do[symbol] = value
del do, dc
