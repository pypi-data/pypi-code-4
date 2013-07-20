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
import os
import socket
import random
import time
import json
import platform

import axonchisel.fuzzytourney.error as error


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
    def _config_req(self, key):
        """Return param from config dict, or raise error if missing."""
        if key not in self._config:
            raise error.ConfigIncompleteError("Missing config param '{0}' in lens '{1}'.".
                format(key, self.__class__.__name__))
        return self._config[key]


# ----------------------------------------------------------------------------



# ----------------------------------------------------------------------------
# Miscellaneous

class LensFunction_Inline(LensFunctionBase):
    """
    Take data directly from tournament data.
    Useful for debugging and developing tournaments, 
    or for hardcoding algorithm constants.
    Config example: { "data": [10, 20, 50, 30, 7, 90] }
    Required param "data" is used as lens data.
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._data = self._config_req('data')
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return self._data

class LensFunction_Interactive_JSON(LensFunctionBase):
    """
    Read JSON from interactive user input.
    Mostly useful for debugging and developing tournaments.
    Config example: { "prompt": "Specify foo: " }
    Optional config "prompt" overrides default input prompt.
    """
    DEFAULT_PROMPT = 'AXFT LENS INTERACTIVE JSON\nINPUT> '
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._prompt = config.get('prompt', self.DEFAULT_PROMPT)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        s = raw_input(self._prompt)
        return json.loads(s)


# ----------------------------------------------------------------------------
# Entrant subsets

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


# ----------------------------------------------------------------------------
# Random

class LensFunction_Random(LensFunctionBase):
    """
    Generate a list of random numbers [0..1).
    Config example: { "count": 4 }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._count = self._config_req('count')
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
        self._count = self._config_req('count')
        self._min = self._config_req('min')
        self._max = self._config_req('max')
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [random.randint(self._min, self._max) for x in range(self._count)]


# ----------------------------------------------------------------------------
# Date and Time

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


# ----------------------------------------------------------------------------
# System/Platform

class LensFunction_UName(LensFunctionBase):
    """
    Returns a fairly portable "uname" tuple of strings:
    (system, node, release, version, machine, processor)
    identifying the underlying platform.
    Config example: { "params": [0, 3] }
    Optional config "params" returns only specific indexed (0-based) entries.
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._params = config.get('params', None)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        uname = platform.uname()
        if self._params is not None:
            uname = [x[1] for x in enumerate(uname) if x[0] in [0, 3]]
        return uname

class LensFunction_HostName(LensFunctionBase):
    """
    Return hostname of computer.
    """
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [socket.gethostname()]

class LensFunction_Env(LensFunctionBase):
    """
    Returns a list of environment variables as strings.
    Missing values are returned as None.
    Config example: { "vars": ["PATH", "HOME"] }
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._vars = self._config_req('vars')
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [os.getenv(v) for v in self._vars]

class LensFunction_Pid(LensFunctionBase):
    """
    Returns numeric process ID of running app.
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [os.getpid()]

class LensFunction_Pwd(LensFunctionBase):
    """
    Returns present working directory.
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [os.getcwd()]


