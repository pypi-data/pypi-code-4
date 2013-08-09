#!/usr/bin/env python3
"""
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains abstract base classes for
sequences and mappings that are built on the standard
Python collection ABCs, but with some additional features.

This sub-package also contains additional collection classes
with method names redefined for greater convenience. The
key desire here is to have the method names 'append' and
'next' refer to the methods that you *want* to call for
each collection to add and retrieve an item from the
"right" place (i.e., the "next" item for the given
collection). Thus:

``fifo`` -- a ``deque``; ``append`` adds to the end of the queue,
    ``nextitem`` retrieves from the start (i.e., ``popleft``).

``stack`` -- a ``list``; ``append`` adds to the end of the list,
    ``nextitem`` retrieves from the end as well (i.e., ``pop``).

There is also an alternate implementation of ``namedtuple``
provided, which does not use a class template. In addition,
an enhanced ``typed_namedtuple`` factory function is provided,
which adds specification of the types of each argument.

Finally, two "utility" collection classes are provided,
``AttrDict`` and ``AttrList``; these allow mapping values
or sequence items to be accessed via attribute names as
well as by the normal subscripting syntax.
"""

from collections import deque

from ._utils import *
from ._abc import *
from ._mixins import *
from ._bases import *
from ._tuples import *


def merge_dict(target, source):
    """Merges source into target
    
    Only updates keys not already in target.
    """
    
    merges = dict((key, value) for key, value in source.items()
                  if key not in target)
    target.update(merges)


class fifo(deque):
    """A first-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.nextitem = self.popleft
        deque.__init__(self, *args, **kwargs)


class stack(list):
    """A last-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.nextitem = self.pop
        list.__init__(self, *args, **kwargs)


class AttrDelegate(object):
    """Delegate attribute access to an underlying object.
    """
    
    def __init__(self, obj):
        self._o = obj
    
    def __getattr__(self, name):
        # Delegate to the underlying object
        return getattr(self._o, name)


class AttrDict(AttrDelegate, basekeyed):
    """Make an object with attributes support a mapping interface.
    
    Only attributes defined in the attribute list passed to this
    class will appear as allowed keys in the mapping. The
    mapping is immutable (since it is only supposed to be
    "assigned" to during initialization).
    """
    
    def __init__(self, keylist, obj):
        AttrDelegate.__init__(self, obj)
        self._keys = keylist
    
    def _keylist(self):
        return self._keys
    
    def _get_value(self, key):
        return getattr(self, key)


class AttrList(AttrDelegate, basecontainer):
    """Make an object with attributes support a sequence interface.
    
    Only indexes in a valid range for the list of attribute names
    passed in will be valid indexes into the sequence (each index
    will access the attribute with the corresponding name in the
    list of names passed in). The sequence is immutable.
    """
    
    def __init__(self, names, obj):
        AttrDelegate.__init__(self, obj)
        self._names = names
    
    def _indexlen(self):
        return len(self._names)
    
    def _get_data(self, index):
        return getattr(self, self._names[index])
