#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A data parser module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'


class BaseParser(object):
    """
    An abstract parser class
    """
    def parse(self, iterable, **kwargs):
        """
        Parse iterable to an numpy array

        Subclass must override this method

        Args:
            iterable: an iterable instance
            **kwargs: optional arguments

        Returns:
            An instance of numpy array
        """
        raise NotImplementedError("Subclass must override this method")

    def load(self, filename, **kwargs):
        """
        Parse a file specified with the filename and return an numpy array

        Args:
            filename: a path of a file
            **kwargs: optional arguments

        Returns:
            An instance of numpy array
        """
        with open(filename, 'r') as f:
            return self.parse(f, **kwargs)
