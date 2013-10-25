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

"""This module contains the game class."""

import curses

class Game(object):
    """This is the main instance in a game

    It holds all the other stuff that belongs to the game, like the
    Map and the InputHandler.

    """
    def __init__(self, map, inp, logsize):
        """Initialize the game instance."""
        self.map = map
        map.game = self
        self.inp = inp
        self.end = False
        self.logsize = logsize

    def logwrite(self, text):
        """Write text to the log"""
        self.log.addstr(self.log.getmaxyx()[0] - 1, 0, text)
        self.log.scroll()
        self.log.refresh()

    def refresh(self, screen, fullwin):
        """Refresh the screen. This happens automatically. You
        don't need to call it."""
        fullmaxx, fullmaxy = fullwin.getmaxyx()
        padmaxx, padmaxy = screen.getmaxyx()
        maxx = min(fullmaxx, padmaxx)
        maxy = min(fullmaxy, padmaxy)
        maxx -= 1
        maxy -= 1
        lookon = self.map.lookon
        try:
            lookpoint = lookon.pos
        except AttributeError:
            # lookon isn't a valid Obj.
            lookpoint = (0, 0)
        mapsx = maxx // 2
        mapsy = (maxy - self.log.getmaxyx()[1]) // 2
        screen.refresh(lookpoint[1] - mapsx, lookpoint[0] - mapsy, 0,
                       self.log.getmaxyx()[1], maxx, maxy) 

    def loop(self, screen, fullwin):
        """Carrie out one step of the game. This is automatically
        called after the call to start. You don't need to call
        this."""
        self.map.print()
        self.refresh(screen, fullwin)
        self.inp.get_input()
        self.map.do_aloop()
        r = self.subloop()
        return r

    def subloop(self):
        """This function gives space for things that happen every
        frame without overriding loop."""
        return True
    
    def user_setup(self):
        """This is called on the end of __init__ and gives space for
        further initialization."""
        pass

    def run(self, screen, fullwin, log):
        """This runs the game. Don't call this. Call start instead."""
        self.map.screen = screen
        self.inp.screen = screen
        self.log = log
        self.user_setup()
        while True:
            r = self.loop(screen, fullwin)
            if (not r) or self.end:
                break

    def start(self):
        """Start the game."""
        padwrap(self.run, self.map.x, self.map.y, self.logsize)

    def set_end(self, _ = None):
        """End the game at the next round."""
        self.end = True

def padwrap(f, xsize, ysize, logx):
    """Initialize a curses screen divided in a pad for the map and a
    log."""
    try:
        fullwin = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED,     curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN,   curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE,    curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN,    curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE,   curses.COLOR_BLACK)
        pad = curses.newpad(ysize + 1, xsize + 1)
        log = curses.newwin(fullwin.getmaxyx()[0], logx)
        log.scrollok(True)
        curses.noecho()
        curses.cbreak()
        orig = curses.curs_set(0)
        pad.keypad(1)
        f(pad, fullwin, log)
    finally:
        curses.nocbreak()
        try:
            pad.keypad(0)
        except NameError:
            pass
        curses.echo()
        try:
            curses.curs_set(orig)
        except:
            pass
        curses.endwin()
