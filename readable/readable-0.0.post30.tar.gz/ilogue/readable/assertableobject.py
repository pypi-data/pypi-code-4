#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>


class AssertableObject():

    def __init__(self, actual):
        self.actual = actual

    def hasValue(self, expected):
        assert expected.matches(self.actual), expected.matchFor(self.actual)

if __name__ == '__main__':
    print(__doc__)
