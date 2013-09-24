#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>


class ConfigurableMethod(object):

    def __init__(self, mockMethod):
        self.__inner = mockMethod

    def toReturnInOrder(self, *returnValues):
        returnValues = [v for v in returnValues]
        returnValues.reverse()

        def side_effect(*args, **kwargs):
            return returnValues.pop()

        self.__inner.side_effect = side_effect

    def toReturn(self, returnValue):
        self.__inner.return_value = returnValue


if __name__ == '__main__':
    print(__doc__)
