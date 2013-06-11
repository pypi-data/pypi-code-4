#This file is part of the M30W software.
#Copyright (C) 2012-2013 M30W developers.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

import time

from math import sqrt, sin, cos, tan, asin, acos, atan, log, log10, e
from random import randrange, uniform
from M30W.debug import debug, not_implemented, ensure_kurt
from M30W.scripts import Script, Block, StopScript, StopScriptsExecution
try:
    import kurt
except ImportError:
    pass


functions = {'sqrt': sqrt,
             'abs': abs,
             'sin': sin,
             'cos': cos,
             'tan': tan,
             'asin': asin,
             'acos': acos,
             'atan': atan,
             'ln': log,
             'log': log10,
             'e ^': lambda x: e ** x,
             '10 ^': lambda x: 10 ** x}


class Base(object):
    kwords = {'costumes': lambda: [],
              'costume': lambda: 0,
              'code': lambda: "",
              'vars': lambda: {},
              'lists': lambda: {},
              'volume': lambda: 100}

    blocks = {}
    def block(name, blocks=blocks):
        def decorator(method):
            method.func_name = name
            blocks[name] = method
        return decorator

    def __init__(self, name, **kwargs):
        """Base(self, name, costumes=[], costume=0, code="", vars={}, lists={},
                volume=100)

        :Parameters:
        - `name`, `costumes`,`costume`, `code`, `vars`,
          `lists`, `volume`
        """
        debug("Creating sprite %s" % name)
        self._name = name

        # Functions because shared mutable objects
        for kword in self.kwords:
            if kword in kwargs: setattr(self, '_' + kword, kwargs[kword])
            else: setattr(self, '_' + kword, self.kwords[kword]())

        self.scripts = {}
        "Compiled scripts stored for caching."

        self._sounds_backup = kwargs['sounds'] if 'sounds' in kwargs else None

    def __repr__(self):
        return "<Sprite '%s' at %s>" % (self.name, id(self))

    def __getattr__(self, key):
        if key in self.blocks:
            return self.blocks[key].__get__(self, self.__class__)
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, key))

    @classmethod
    def from_kurt(cls, morph):
        raise NotImplementedError

    def to_kurt(self):
        raise NotImplementedError

    def compile_scripts(self):
        """Compile scripts and bind them to events."""
        ensure_kurt()
        #TODO: Compile scripts using own code.
        code = unicode(self.code).split('\n' * 3)
        code = [sheet for sheet in code if sheet.strip("\r\n ")]
        try:
            parsed_scripts = map(kurt.parse_block_plugin, code)
        except SyntaxError:
            raise SyntaxError(code)
        self.scripts = {event: script for event, script in
                        map(lambda s:Script.from_kurt(s, self), parsed_scripts)}
        from M30W.runtime import engine
        for event, script in self.scripts.iteritems():
            engine.bind(event, script)

    #Called from children, to reduce code be rewritten.
    def set_kurt_attrs(self, morph):
        morph.images = [costume.to_kurt() for costume in self._costumes]
        morph.costume = morph.images[self._costume]
        lists = {}
        for name, list in self._lists.iteritems():
            lists[name] = kurt.ScratchListMorph(name=name, items=list)
        morph.lists = lists
        morph.vars = self._vars.copy()  # I don't trust kurt :)
        morph.volume = self._volume

        if self._sounds_backup:
            morph.sounds = self._sounds_backup

        code = unicode(self.code).split('\n' * 3)
        code = [sheet for sheet in code if sheet.strip("\r\n ")]
        for sheet in code:
            sheet = kurt.parse_block_plugin(sheet)
            sheet.morph = morph
            sheet.pos = kurt.Point([20, 20])
            morph.scripts.extend([sheet])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def vars(self):
        return self._vars

    @property
    def lists(self):
        return self._lists

    @property
    def costumes(self):
        return self._costumes

    @property
    def costume(self):
        return self._costume

    @costume.setter
    def costume(self, value):
        self.costumes[value]  # Validate that index is in range
        self._custume = value

    @property
    def active_costume(self):
        return self.costumes[self.costume]

    @active_costume.setter
    def active_costume(self, value):
        self.costume = self.costumes.index(value)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        value = float(value)
        if not 0 <= value <= 100:
            raise TypeError("Value must bew in range 0-100")
        self._volume = value

    @property
    def is_stage(self):
        return self.name == 'Stage'

    # Sounds support comes later.

    #==========================================================================
    # Begin blocks code
    #==========================================================================

    ### Escape methods ###

    @staticmethod
    def number(i):
        if isinstance(i, Block):
            i = i()
        return float(i)
        #TODO: Add Scratch's number escaping "capabilities"

    @staticmethod
    def string(i):
        if isinstance(i, Block):
            i = i()
        return str(i)

    ### Control blocks ###

    @block('wait:elapsed:from:')
    def _(self, seconds):
        exec_time = time.time()
        while not exec_time - time.time() > self.number(seconds):
            yield

    @block('doForever')
    def _(self, block):
        while True:
            for _ in block(): yield

    @block('doRepeat')
    def _(self, times, block):
        for _ in xrange(times):
            for _ in block(): yield

    @block('broadcast:')
    def _(self, broadcast):
        pass

    @block('doBroadcastAndWait')
    def _(self, broadcast):
        pass

    @block('doForeverIf')
    def _(self, predicate, block):
        while True:
            if predicate():
                for _ in block(): yield
            else: yield

    @block('doIf')
    def _(self, condition, block):
        if condition():
            for _ in block(): yield

    @block('doIfElse')
    def _(self, condition, block, else_block):
        if condition():
            for _ in block(): yield
        else:
            for _ in block(): yield

    @block('doWaitUntil')
    def _(self, predicate):
        while not predicate(): yield

    @block('doUntil')
    def _(self, predicate, block):
        while not predicate():
            for _ in block: yield

    @block('doReturn')
    def _(self):
        raise StopScript

    @block('stopAll')
    def _(self):
        raise StopScriptsExecution

    ### Operators blocks ###
    #Numbers
    block('+')(lambda self, a, b: self.number(a) + self.number(b))
    block('-')(lambda self, a, b: self.number(a) - self.number(b))
    block('*')(lambda self, a, b: self.number(a) * self.number(b))
    block('/')(lambda self, a, b: self.number(a) / self.number(b))

    @block('randomFrom:to:')
    def _(self, a, b):
        try:
            return randrange(self.number(a), self.number(b))
        except ValueError:
            return uniform(self.number(a), self.number(b))

    #Booleans
    # The behaviour of those blocks isn't very clear and is different in flash.
    # I implemented the flash version
    @block('>')
    def _(self, a, b):
        try:
            return self.number(a) > self.number(b)
        except ValueError:
            return self.string(a) > self.string(b)

    block('=')(lambda self, a, b: a == b)

    @block('<')
    def _(self, a, b):
        try:
            return self.number(a) < self.number(b)
        except ValueError:
            return self.string(a) < self.string(b)

    block('&')(lambda self, a, b: a and b)
    block('|')(lambda self, a, b: a or b)
    block('not')(lambda self, a: not a)

    #Strings
    block('concatenate:with:')(lambda self, a, b: self.string(a) +
                                                  self.string(b))
    block('letter:of:')(lambda self, index, string:
                            self.string(string)[self.number(index)])
    block('stringLength:')(lambda self, string: len(self.string(string)))

    #Math functions
    @block(r'\\')
    def _(self, a, b):
        return a % b

    @block('rounded')
    def _(self, a):
        return round(a)

    @block('computeFunction:of:')
    def _(self, function, a):
        a = self.number(a)
        return functions[function](a)

    ### Looks Blocks ###
