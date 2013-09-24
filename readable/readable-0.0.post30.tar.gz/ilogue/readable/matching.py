#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

from ilogue.readable.xmlmatcher import XmlMatcher
from ilogue.readable.alchemymatcher import AlchemyMatcher
from ilogue.readable.datetimematcher import DatetimeMatcher
from ilogue.readable.stringmatcher import StringMatcher
from ilogue.readable.LinkMatcher import LinkMatcher
from ilogue.readable.FragmentMatcher import FragmentMatcher
from ilogue.readable.GeneralMatcher import GeneralMatcher


def that():
    return MatcherFactory()


class MatcherFactory(object):

    def isXmlElement(self):
        return XmlMatcher()

    def isAnything(self):
        return GeneralMatcher().anything()

    def hasSameIdAs(self, expected):
        return AlchemyMatcher(expected)

    def isDateTime(self):
        return DatetimeMatcher()

    def isString(self):
        return StringMatcher()

    def isLink(self):
        return LinkMatcher()

    def isFragment(self):
        return FragmentMatcher()
