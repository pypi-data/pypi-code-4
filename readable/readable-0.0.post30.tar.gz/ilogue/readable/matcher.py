#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>


class Matcher(object):

    def matches(self, other):
        return self.matchFor(other).successful

    def matchFor(self, other):
        raise NotImplementedError('Should be implemented by child class.')
