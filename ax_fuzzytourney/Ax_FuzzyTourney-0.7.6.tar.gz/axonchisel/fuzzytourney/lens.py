"""
Ax_FuzzyTourney - lens functions.

The lens function takes a single entrant and reveals a list of data.
Elements of this produced list are subsequently map/reduced by judges using
configurable heuristics down into scores (criteria).

This module is not intended for public use.
User lenses (subclass LensFunction) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import sys
import random
import time


# ----------------------------------------------------------------------------


class LensFunction(object):
    """Lens function superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class LensFunctionBase(LensFunction):
    """Base superclass for Lens functions."""
    def __init__(self, config):
        self._config = config


# ----------------------------------------------------------------------------


class LensFunction_Entrant_Slice(LensFunctionBase):
    """
    Extract a slice of a list entrant.
    Uses Python list slicing notation including support for negative values.
    Config example: { "start": 1, "stop": 2, "step": 1 }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._start = config.get('start', None)
        self._stop = config.get('stop', None)
        self._step = config.get('step', 1)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return entrant[self._start:self._stop:self._step]

class LensFunction_Entrant_Keys(LensFunctionBase):
    """
    Extract a list of values by keys from a dict entrant.
    Config example: { "keys": ["foo", "bar"] }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._keys = config.get('keys', list())
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [entrant[k] for k in self._keys]

class LensFunction_Random(LensFunctionBase):
    """
    Generate a list of random numbers [0..1).
    Config example: { "count": 4 }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._count = config['count']
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [random.random() for x in range(self._count)]

class LensFunction_RandomInt(LensFunctionBase):
    """
    Generate a list of random numbers [min..max].
    Config example: { "count": 4, "min": 1, "max": 10 }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._count = config['count']
        self._min = config['min']
        self._max = config['max']
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [random.randint(self._min, self._max) for x in range(self._count)]

class LensFunction_DateTime(LensFunctionBase):
    """
    Generate the current time as UTC datetime object.
    """
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [time.gmtime()]

class LensFunction_Time_t(LensFunctionBase):
    """
    Generate the current time as seconds from epoch.
    Optionally adjust "whole" (default True) to allow fractional seconds through.
    Config example: { "whole": True }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._whole = config.get('whole', True)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        t = time.time()
        if self._whole:
            t = int(t)
        return [t]


