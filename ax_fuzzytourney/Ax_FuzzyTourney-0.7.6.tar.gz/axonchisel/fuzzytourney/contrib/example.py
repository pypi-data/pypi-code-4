"""
Ax_FuzzyTourney - example 3rd party extensions.

This module is an example of how to incorporate 3rd party extensions.
These may be used in place of standard input formats, output formats,
lens functions, map functions, and reduce functions.
Reference custom functions by using the full dotted path to class in 
tournament config.

Note that currently there are no input, output, field, or select examples
here, but those components are all possible to extend similarly.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import random

from axonchisel.fuzzytourney.input import InputFormatBase
from axonchisel.fuzzytourney.output import OutputFormatBase
from axonchisel.fuzzytourney.field import OutputFieldFunctionBase
from axonchisel.fuzzytourney.select import SelectFunctionBase
from axonchisel.fuzzytourney.lens import LensFunctionBase
from axonchisel.fuzzytourney.map import MapFunctionBase
from axonchisel.fuzzytourney.reduce import ReduceFunctionBase


# ----------------------------------------------------------------------------


class MyLensFunction_Numerology(LensFunctionBase):
    """
    Example lens function that gives alaphabetic placement number
    for each character in entrant string.
    E.g. "Andy" results in [1, 14, 4, 25].
    Config eg: { "base": 0 }
    Specify optional "base" config to add amount to each value.
    """
    def __init__(self, config):
        LensFunctionBase.__init__(self, config)
        self._base = config.get('base', 0)
    def execute(self, entrant):
        """Abstract: Execute lens func on one entrant, and return values."""
        return [self._base + ord(c.lower()) - ord('a') + 1 for c in entrant]

class MyMapFunction_MultipleMaker(MapFunctionBase):
    """
    Rounds values (down) to the nearest multiple of specified number.
    Config eg: { "factor": 2 }
    E.g. [1, 2, 3, 5, 8] with factor 2 results in [0, 2, 2, 4, 8].
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._factor = config['factor']
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return (data1)/self._factor*self._factor

class MyReduceFunction_MostMagical(ReduceFunctionBase):
    """
    Reduce function that finds the "most magical" value.
    Config eg: { "special": [7, 8] }
    Actually finds first number with any of "special" digits in it.
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
        self._special = config['special']
    def execute(self, data):
        if len(data) == 0:
            return 0
        for d1 in data:
            for c in self._special:
                if str(c) in str(d1):
                    return d1
        return data[0]
