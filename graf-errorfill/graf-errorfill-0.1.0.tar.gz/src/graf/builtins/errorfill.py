#!/usr/bin/env python
# coding=utf-8
"""

(C) 2013 hashnote.net, Alisue
"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
__date__    = '2013-10-10'

from mpltools.special import errorfill as _errorfill
from graf.builtins.pyplot import original_color_cycle

errorfill = original_color_cycle(_errorfill)
