#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A text data parser module

(C) 2013 hashnote.net, Alisue
"""
import numpy as np
from graf.parser import BaseParser

class PlainParser(BaseParser):
    """
    A plain text parser class based on `numpy.loadtxt` method
    """
    def parse(self, iterable, **kwargs):
        """
        Parse whitespace separated iterable to an numpy array.
        It is based on `numpy.loadtxt` method.

        Args:
            iterable: an iterable instance
            **kwargs: optional arguments

        Returns:
            An instance of numpy array
        """
        return np.loadtxt(iterable, **kwargs)
