#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A JASCO data parser module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
import numpy as np
from graf.parser import BaseParser


class JASCOParser(BaseParser):
    """
    A JASCO parser class
    """
    def parse(self, iterable, delimiter=None, **kwargs):
        """
        Parse JASCO style iterable to an numpy array

        Args:
            iterable: an iterable instance
            delimiter: a delimiter character (Default: None).
                whitespaces include tab character is used in default
            **kwargs: optional arguments

        Returns:
            An instance of numpy array
        """
        d = []
        datamode = False
        for r in iterable:
            r = r.strip()
            c = r.split(delimiter)
            if datamode and len(r) == 0 or c[0] == '':
                break
            if datamode:
                d.append(c)
            elif c[0] == 'XYDATA':
                datamode = True
        # probably all data is numeric in JASCO txt format but I'm not sure...
        d = np.array(d, dtype=kwargs.get('dtype', float))
        return d

    def load(self, filename, delimiter=None, **kwargs):
        """
        Parse a file specified with the filename and return an numpy array

        Args:
            filename: a path of a file
            delimiter: a delimiter character (Default: None).
                whitespaces include tab character is used in default
            **kwargs: optional arguments

        Returns:
            An instance of numpy array
        """
        if filename.lower().endswith('.csv'):
            delimiter = delimiter or ','
        return super(JASCOParser, self).load(
                filename, delimiter=delimiter, **kwargs)
