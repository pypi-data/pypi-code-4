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

"""This module contains the Map class, which holds the Onjs in the game."""

from .field import Field
from .character import Obj
import locale

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

class Map(dict):
    """This class holds all the Objs in the game.

    It also manages the action-loop

    """
    def __init__(self, size):
        self.x, self.y = size
        self.screen = None
        for j in range(self.y):
            for i in range(self.x):
                self[i, j] = Field(i, j)
        self.lookon = None
        self.aloop = []
        self.game = None

    __repr__ = object.__repr__
    __str__ = object.__str__

    def print(self):
        #debug = open('lesspipe.pipe', 'w')
        for j in range(self.y):
            for i in range(self.x):
                obj = self[i, j]
                color = obj.color()
                #print(color(), file = debug)
                self.screen.addstr(j, i, str(obj), color())

    def place(self, obj, x, y, actions=False):
        "Places obj on the map on x, y."
        if not isinstance(obj, Obj):
            raise TypeError("obj must be a subclass of Character")
        self[x, y].append(obj)
        obj.pos = x, y
        obj.map = self
        if actions:
            self.aloop.append(obj)

    def remove(self, obj, x, y):
        field = self[x, y]
        field.remove(obj)

    def do_aloop(self):
        for ai in self.aloop:
            ai.aloop()
