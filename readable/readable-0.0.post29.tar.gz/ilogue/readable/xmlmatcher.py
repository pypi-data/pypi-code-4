#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

from ilogue.readable.matcher import Matcher
import xml.etree.ElementTree


class XmlMatcher(Matcher):
    ID_ATTRIB = "id"

    def __init__(self):
        super(XmlMatcher, self).__init__()
        self.__tag = None
        self.__txt = None
        self.__id = None

    def withTag(self, tagString):
        self.__tag = tagString
        return self

    def withText(self, textString):
        self.__txt = textString
        return self

    def withId(self, idString):
        self.__id = idString
        return self

    def matchFor(self, other):
        if not self.isXml(other):
            return XmlMatch().isNotXml(other)
        if self.__tag:
            if self.__tag != other.tag:
                return XmlMatch().isTagMisMatch(self.__tag, other.tag)
        if self.__txt:
            if self.__txt != other.text:
                return XmlMatch().isTextMisMatch(self.__txt, other.text)
        if self.__id:
            if self.__id != self.getId(other):
                return XmlMatch().isIdMisMatch(self.__id, self.getId(other))
        return XmlMatch()

    def getId(self, other):
        return other.attrib.get(self.ID_ATTRIB)

    def isXml(self, other):
        return xml.etree.ElementTree.iselement(other)


class XmlMatch(object):
    NOTXMLMSG = "Object ({0}) is not an xml element."
    FAILMSG = ("Xml Element has a different {2} " +
        "({0}) than expected ({1}).")

    def isNotXml(self, other):
        self.__success = False
        self.__msg = self.NOTXMLMSG.format(other)
        return self

    def isTagMisMatch(self, exp, act):
        self.__success = False
        self.__msg = self.FAILMSG.format(act, exp, 'tag')
        return self

    def isTextMisMatch(self, exp, act):
        self.__success = False
        self.__msg = self.FAILMSG.format(act, exp, 'content')
        return self

    def isIdMisMatch(self, exp, act):
        self.__success = False
        self.__msg = self.FAILMSG.format(act, exp, 'id')
        return self

    def __init__(self):
        self.__success = True
        self.__msg = "Successful Xml Match."

    @property
    def successful(self):
        return self.__success

    def __str__(self):
        return self.__msg
