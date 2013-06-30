# -*- coding: iso-8859-1 -*- #
# ======================================================================
#
# Copyright (C) 2013 Kay Schluehr (kay@fiber-space.de)
#
# t3.pattern.py, v B.0 2013/09/03
#
# ======================================================================

import abc

class T3Matcher:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def is_variable(self):
        return False

    @abc.abstractmethod
    def get_value(self):
        pass

    @abc.abstractmethod
    def match(self, data):
        pass


class T3Value:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_value(self):
        pass

