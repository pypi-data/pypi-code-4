#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# wrapper for pymock

from ilogue.readable.matcher import Matcher
from ilogue.readable.ContextProviderMock import ContextProviderMock

class AssertableContext(object):

    def __init__(self, contextProvider):
        if not isinstance(contextProvider, ContextProviderMock):
            raise TypeError('Can only assert ContextProviderMock.')
        assert contextProvider.context.wasEntered, "Mocked context was not entered." 


if __name__ == '__main__':
    print(__doc__)
