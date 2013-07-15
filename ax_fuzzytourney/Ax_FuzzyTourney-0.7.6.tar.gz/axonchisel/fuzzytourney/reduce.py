"""
Ax_FuzzyTourney - reduce functions.

The list of elements produced by a lens function (for a single competitor)
have the map function applied to each by judges using configurable heuristics
prior to being reduced to a single value by a reduce function and
applied as scores (criteria).

This module is not intended for public use.
User reducers (subclass ReduceFunction) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import math


# ----------------------------------------------------------------------------


class ReduceFunction(object):
    """Reduce function superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class ReduceFunctionBase(ReduceFunction):
    """Base superclass for Reduce functions."""
    def __init__(self, config):
        self._config = config


# ----------------------------------------------------------------------------


class ReduceFunction_First(ReduceFunctionBase):
    """
    Reduce function that returns first value.
    """
    def execute(self, data):
        if len(data) == 0:
            return 0
        return data[0]

class ReduceFunction_Zero(ReduceFunctionBase):
    """
    Reduce function that returns 0, disregarding all values.
    """
    def execute(self, data):
        return 0

class ReduceFunction_Ignore(ReduceFunction_Zero):
    """
    Reduce function that ignores all data, returning 0.
    """
    pass

class ReduceFunction_Sum(ReduceFunctionBase):
    """
    Return sum of all numeric values.
    """
    def execute(self, data):
        if len(data) == 0:
            return 0
        return sum(data)

class ReduceFunction_Min(ReduceFunctionBase):
    """
    Return lowest numeric value.
    """
    def execute(self, data):
        if len(data) == 0:
            return 0
        return min(data)
            
class ReduceFunction_Max(ReduceFunctionBase):
    """
    Return highest numeric value.
    """
    def execute(self, data):
        if len(data) == 0:
            return 0
        return max(data)

class ReduceFunction_Mean(ReduceFunctionBase):
    """
    Average numeric values.
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        if len(data) == 0:
            return 0
        return sum(data) / float(len(data))

class ReduceFunction_MaxMeanDeviation(ReduceFunctionBase):
    """
    Averages numeric values, and return the largest absolute distance of
    any value from the calculated mean.
    Config example: { "normalize": true }
    Optional config param "normalize" divides resulting distance by mean.    
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
        self._normalize = config.get('normalize', False)
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        if len(data) == 0:
            return 0
        mean = sum(data) / float(len(data))
        maxdist = max([abs(d - mean) for d in data])
        if self._normalize:
            if mean == 0:
                return 0
            return abs(maxdist / mean)
        return maxdist

class ReduceFunction_StandardDeviation(ReduceFunctionBase):
    """
    Return standard deviation of values.
    See https://en.wikipedia.org/wiki/Standard_deviation
    Config example: { "normalize": true }
    Optional config param "normalize" divides resulting value by mean.    
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
        self._normalize = config.get('normalize', False)
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        if len(data) == 0:
            return 0
        mean = sum(data) / float(len(data))
        dists_sq = [(d - mean)**2 for d in data]
        avg_dists_sq = sum(dists_sq) / len(dists_sq)
        stddev = math.sqrt(avg_dists_sq)
        return stddev

class ReduceFunction_MaxChangeRate(ReduceFunctionBase):
    """
    Compares each numeric item to previous non-null, resulting in 0=no change,
    to 1=100pct change, etc. Always positive result and does not take into
    consideration direction of change.
    Returns largest change amount of all comparisons.
    Config example: { "zero_as": 10, "zero_size": 0.001 }
    If 0 appears in input data non-terminal position, resulting change to next
    value would be infinite, so config "zero_as" defined equivalent value used
    for zero for purpose of comparison, or null to treat all 0 values as
    gaps that reset detection.
    Config "zero_size" defines what is considered 0 to begin with, useful
    to grab very small numbers since floats may lose data during calculations.
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
        self._zero_as = config.get('zero_as', 0.00000001)
        self._zero_size = config.get('zero_size', 0.00000001)
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        if len(data) == 0:
            return 0
        changes = []
        prev = data[0]
        for d in data[1:]:
            if d is None:
                continue
            if abs(d) < self._zero_size:
                if self._zero_as is None:
                    continue
            if prev is None:
                prev = d
                continue
            prev_cmp = prev
            d_cmp = d
            prev = d
            if abs(prev_cmp) <= self._zero_size:
                if self._zero_as is None:
                    continue
                prev_cmp += self._zero_as
                d_cmp += self._zero_as
            ch = abs(float(d_cmp - prev_cmp) / float(prev_cmp))
            changes.append(ch)
        if len(changes) == 0:
            return 0
        return max(changes)

