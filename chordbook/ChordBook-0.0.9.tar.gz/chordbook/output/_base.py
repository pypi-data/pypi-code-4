# _base.py

# Base class for ChordBook outputters

import chordbook.libcbk

class CbkOutputter(object):

    def __init__(self):
        pass


    def make_book(self, b):
        """Output internal representation of Book object"""
        print repr(b);
