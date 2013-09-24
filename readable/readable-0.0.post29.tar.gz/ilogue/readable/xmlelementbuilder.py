#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# creates xml elements for testing purposes

import unittest
import xml.etree.ElementTree as ElementTree


class XmlElementBuilder(object):

    def __init__(self, tagName):
        self.__inner = ElementTree.Element(tagName)

    def build(self):
        return self.__inner

    def withoutId(self):
        return self

    def withId(self, idString):
        self.__inner.set("id", idString)
        return self

    def withNameAttribute(self, nameString):
        self.__inner.set("name", nameString)
        return self

    def withAttribute(self, attributeName, attributeValue):
        self.__inner.set(attributeName, attributeValue)
        return self

    def withSimpleChild(self, tagName, textValue):
        child = ElementTree.Element(tagName)
        child.text = textValue
        self.__inner.append(child)
        return self

    def withEmptyChild(self, tagName):
        child = ElementTree.Element(tagName)
        self.__inner.append(child)
        return self

    def withChild(self, childBuilder):
        self.__inner.append(childBuilder.build())
        return self


if __name__ == '__main__':
    unittest.main()
