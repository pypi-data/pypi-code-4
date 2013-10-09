#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
Recursive glob module

This glob is a recursive version of `glob` module.

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
__all__ = ['iglob', 'glob']
import os
import fnmatch


def iglob(pathname):
    """
    Return an iterator which yields the same values as glob() without actually
    storing them all simultaneously.
    """
    dirname = os.path.dirname(pathname)
    basename_pattern = os.path.basename(pathname)
    for root, dirs, files in os.walk(dirname):
        for basename in files:
            if fnmatch.fnmatch(basename, basename_pattern):
                yield os.path.join(root, basename)

def glob(pathname):
    """
    Return a possibly-empty list of path names that match pathname.
    It is recursive version of `glob.glob()`
    """
    return list(iglob(pathname))
