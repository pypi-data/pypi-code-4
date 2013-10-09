#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A linestyle module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
from graf.config import settings
from graf.styles import CycleIterator


class LineCycle(CycleIterator):
    """A cycle iterator for line styles"""
    _linestyles = settings['default']['linestyles']

    @property
    def iterable(self):
        return self._linestyles

"""An instance of LineCycle used in entire system"""
linestyle_cycle = LineCycle()
