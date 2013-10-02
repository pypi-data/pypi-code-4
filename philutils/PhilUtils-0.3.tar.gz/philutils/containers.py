#!/usr/bin/env python

# Name: containers.py
# Author: Philip Zerull
# Date Created: Thursday March 1, 2012
# Copyright 2012 Philip Zerull

from copy import deepcopy


def dictapply(basedict, overridedict):
    """Returns a deep copy of basedict, with items overridden by overridedict

    This is similiar to dict.update, only that it acts recursively on
    dictionarys stored as values in basedict.

    WARNING: this does not protect against infinite recursion if a dictionary
    contains a reference to itself.
    """
    outey = deepcopy(basedict)
    for var, value in overridedict.items():
        if isinstance(value, dict):
            if var in outey and isinstance(outey[var], dict):
                outey[var] = dictapply(outey[var], value)
            else:
                outey[var] = deepcopy(value)
        else:
            outey[var] = deepcopy(value)
    return outey


class DotDict(dict):
    """Provides an alternate syntax for dictionaries.

    This is basically javascript structs implemented using python dictionaries.

    This class inherits from dict and thus almost all of its properties and
    methods use the dict class version except, this implementation allows
    the following.

    a = DotDict()
    b = Dict()
    a.banana = 'monkey' <=> b['banana'] = 'monkey'
    a.items = ['bags, 3, dict()] <=> b['items'] = ['bags, 3, dict()]
    a.items() <=> b.items()

    basically, using the dot notation you can set any value to any 'textual'
    key.  You can then get the values of these keys using the dot notation as
    well.  If the key you are setting interferes with a defined attribute of
    the dictionary class (such as items, __len__, keys, etc...) then the
    when getting the value of the reserved key results in the default
    behavior for a dictionary. (DotDict.items referrs to the items method
    of the dictionary class whereas DotDict['items'] referrs to the value
    associated with the key 'items'.
    """

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return dict.__getitem__(self, item)

    def __deepcopy__(self, memodict={}):
        memodict[id(self)] = None
        outey = DotDict()
        for key, value in self.items():
            if isinstance(value, DotDict):
                if id(value) in memodict:
                    raise ValueError('Infinite Recursion Detected')
                else:
                    outey[key] = value.__deepcopy__(memodict)
            else:
                outey[key] = deepcopy(value)
        del memodict[id(self)]
        return outey


class Grid(object):
    """An N dimentional grid object which can contain arbitrary python objects.
    """
    def __init__(self, *each_dimensions_length):
        if len(each_dimensions_length) <= 0:
            raise ValueError('Must have at least one dimension')
        self._dimension_length = list(each_dimensions_length)
        each_dimensions_length = list(each_dimensions_length)
        curtemplate = None
        while len(each_dimensions_length):
            curlen = each_dimensions_length.pop()
            newtemplate = []
            for item in range(curlen):
                newtemplate.append(deepcopy(curtemplate))
            curtemplate = newtemplate
        self._data = curtemplate

    def __getitem__(self, index):
        index = self._validate_index(index)
        curitem = self._data
        for current_index in index:
            curitem = curitem[current_index]
        return curitem

    def _validate_index(self, index):
        if isinstance(index, int):
            index = [index]
        if len(index) != len(self._dimension_length):
            raise ValueError('incorrect number of indexes provided')
        return index

    def __setitem__(self, key, value):
        key = self._validate_index(key)
        curitem = self._data
        for current_index in key[:-1]:
            curitem = curitem[current_index]
        curitem[key[-1]] = value

    def __delitem__(self, index):
        self.__setitem__(index, None)
