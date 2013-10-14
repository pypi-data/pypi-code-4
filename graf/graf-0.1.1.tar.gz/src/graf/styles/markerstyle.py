#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A markerstyle module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
from graf.config import settings
from graf.styles import CycleIterator


class MarkerCycle(CycleIterator):
    """A cycle iterator for marker styles"""
    _markerstyles = settings['default']['markerstyles']

    @property
    def iterable(self):
        return self._markerstyles

"""An instance of MarkerCycle used in entire system"""
markerstyle_cycle = MarkerCycle()
