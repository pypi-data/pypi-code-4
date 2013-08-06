#!/usr/bin/env python

# Name: containers.py
# Author: Philip Zerull
# Date Created: Thursday March 1, 2012
# Copyright 2012 Philip Zerull


class DotDict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return dict.__getitem__(self, item)
