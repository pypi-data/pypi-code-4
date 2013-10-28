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

#This file is part of cursgame 0.1.1

import abc
from . import color

class Obj(metaclass=abc.ABCMeta):
    "Base class for all classes that can be placed on a map"
    def __init__(self):
        self.pos = None
        self.map = None #The map this character is on
        self.dead = False #This marks wether the Obj was killed

    def move(self, xd, yd):
        "Moves the character on the field"
        x, y = self.pos
        tarx = x + xd
        tary = y + yd
        try:
            target = self.map[tarx, tary]
        except KeyError:
            return
        success = True
        if len(target):
            success = target[-1].activate(self, xd, yd)
        if success:
            self.map.remove(self, x, y)            
            self.map.place(self, tarx, tary)

    @abc.abstractmethod
    def __str__(self):
        return " "

    def color(self):
        return color.WHITE

    def activate(self, activater, x, y):
        """Wird aufgerufen wenn etwas gegen das Obj stösst.

        Entfernt das Objekt vom Spielfeld

        """
        self.map.remove(self, *self.pos)
        if self in self.map.aloop:
            self.map.aloop.remove(self)
        self.dead = True
        return True

    def aloop(self):
        """This function is called if the Obj is registered in the
        ailoop of the map"""
        pass

class Human(Obj):
    def __str__(self):
        return "@"

    def color(self):
        return color.BLUE
