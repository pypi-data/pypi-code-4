#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>
from ilogue.readable.matcher import Matcher


class StringMatcher(Matcher):
    expectsContained = None

    def matchFor(self, other):
        if not isinstance(other, str):
            return (StringMatch()
                .isTypeMisMatch(type(other), str))
        if self.expectsContained and not self.expectsContained in other:
            return (StringMatch()
                .doesNotContain(other, self.expectsContained))
        return StringMatch()

    def containing(self, contained):
        self.expectsContained = contained
        return self

    def __str__(self):
        s = "[ that is a string"
        if self.expectsContained:
            s += " containing '" + self.expectsContained + "'"
        s += " ]"
        return s


class StringMatch(object):
    TYPEFAILMSG = "String Object has other type ({0}) than expected ({1})."
    CONTAINFAILMSG = 'String does not contain "{1}": "{0}"'

    def isTypeMisMatch(self, act, exp):
        self.__success = False
        self.__msg = self.TYPEFAILMSG.format(act, exp)
        return self

    def doesNotContain(self, act, exp):
        self.__success = False
        self.__msg = self.CONTAINFAILMSG.format(act, exp)
        return self

    def __init__(self):
        self.__success = True
        self.__msg = "Successful Alchemy Match."

    @property
    def successful(self):
        return self.__success

    def __str__(self):
        return self.__msg
