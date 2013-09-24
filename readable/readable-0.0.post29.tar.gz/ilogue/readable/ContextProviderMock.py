#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>
# wrapper for pymock


class ContextProviderMock(object):

    def __init__(self):
        self.context = ContextMock()

    def __call__(self):
        return self.context

class ContextMock(object):
    wasEntered = False
    wasExited = False

    def __enter__(self):
        self.wasEntered = True

    def __exit__(self,exc_type, exc_val, exc_tb):
        return False

if __name__ == '__main__':
    print(__doc__)
