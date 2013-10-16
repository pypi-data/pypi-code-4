#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   Alisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# Date:     2013-10-08
#
# (C) 2013 hashnote.net, Alisue
#
class Bunch(dict):
    """
    A collector of a bunch of named staff

    Usage:
        >>> bunch = Bunch(a='a', b='b', c='c')
        >>> assert bunch['a'] == 'a'
        >>> assert bunch['b'] == 'b'
        >>> assert bunch['c'] == 'c'
        >>> assert bunch.a == 'a'
        >>> assert bunch.b == 'b'
        >>> assert bunch.c == 'c'
        >>> bunch['a'] = 1
        >>> assert bunch['a'] == 1
        >>> assert bunch.a == 1
        >>> bunch.a = 2
        >>> assert bunch['a'] == 2
        >>> assert bunch.a == 2

    Reference:
        http://code.activestate.com/
    """
    def __init__(self, **kwargs):
        super(Bunch, self).__init__(**kwargs)
        self.__dict__ = self

def unittest():
    import doctest; doctest.testmod()

if __name__ == '__main__':
    unittest()
