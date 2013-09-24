#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>
from ilogue.readable.matcher import Matcher


class AlchemyMatcher(Matcher):

    def __init__(self, expected):
        self.expected = expected
        super(AlchemyMatcher, self).__init__()

    def matchFor(self, other):
        if not type(other) == type(self.expected):
            mismatch = AlchemyMatch()
            mismatch.isTypeMisMatch(type(self.expected), type(other))
            return mismatch
        if other.id != self.expected.id:
            return AlchemyMatch().isIdMisMatch(other.id, self.expected.id)
        return AlchemyMatch()


class AlchemyMatch(object):
    TYPEFAILMSG = "Alchemy Object has other type ({0}) than expected ({1})."
    IDFAILMSG = "Alchemy Object has a different id ({0}) than expected ({1})."

    def isTypeMisMatch(self, exp, act):
        self.__success = False
        self.__msg = self.TYPEFAILMSG.format(act, exp)
        return self

    def isIdMisMatch(self, exp, act):
        self.__success = False
        self.__msg = self.IDFAILMSG.format(act, exp)
        return self

    def __init__(self):
        self.__success = True
        self.__msg = "Successful Alchemy Match."

    @property
    def successful(self):
        return self.__success

    def __str__(self):
        return self.__msg
