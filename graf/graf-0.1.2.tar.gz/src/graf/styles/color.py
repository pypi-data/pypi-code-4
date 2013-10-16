#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A color module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
import matplotlib as mpl
from graf.config import settings
from graf.styles import CycleIterator


class ColorCycle(CycleIterator):
    """A cycle iterator for colors"""

    def __init__(self):
        super(ColorCycle, self).__init__()
        self._colors = settings['default']['colors']

    @property
    def _colors(self):
        return mpl.rcParams['axes.color_cycle']
    @_colors.setter
    def _colors(self, value):
        if value is not None:
            mpl.rcParams['axes.color_cycle'] = value
            self.reset()

    @property
    def iterable(self):
        return self._colors

"""An instance of ColorCycle used in entire system"""
color_cycle = ColorCycle()
