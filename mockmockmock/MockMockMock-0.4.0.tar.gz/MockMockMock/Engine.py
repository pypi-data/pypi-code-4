# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.

import inspect

from _Details.Mock import Mock
from _Details.ExpectationGrouping import OrderedExpectationGroup, UnorderedExpectationGroup, AtomicExpectationGroup, OptionalExpectationGroup, AlternativeExpectationGroup, RepeatedExpectationGroup
from _Details.ExpectationHandler import ExpectationHandler


class Engine:
    def __init__(self):
        self.__handler = ExpectationHandler(OrderedExpectationGroup())
        self.__replaced = []

    def create(self, name):
        return Mock(name, self.__handler)

    def replace(self, name):
        container, attribute = self.__findByName(name)
        self.__replaced.append((container, attribute, getattr(container, attribute)))
        m = self.create(name)
        setattr(container, attribute, m.object)
        return m

    @staticmethod
    def __findByName(name):
        names = name.split(".")
        attribute = names[-1]
        current = inspect.currentframe()
        try:
            frame = current.f_back.f_back
            symbols = dict(frame.f_globals)
            symbols.update(frame.f_locals)
            container = symbols[names[0]]
        finally:
            del current
        for name in names[1:-1]:
            container = getattr(container, name)
        return container, attribute

    def tearDown(self):
        for container, attribute, value in self.__replaced:
            setattr(container, attribute, value)
        self.__handler.tearDown()

    @property
    def unordered(self):
        return self.__handler.pushGroup(UnorderedExpectationGroup())

    @property
    def ordered(self):
        return self.__handler.pushGroup(OrderedExpectationGroup())

    @property
    def atomic(self):
        return self.__handler.pushGroup(AtomicExpectationGroup())

    @property
    def optional(self):
        return self.__handler.pushGroup(OptionalExpectationGroup())

    @property
    def alternative(self):
        return self.__handler.pushGroup(AlternativeExpectationGroup())

    @property
    def repeated(self):
        return self.__handler.pushGroup(RepeatedExpectationGroup())
