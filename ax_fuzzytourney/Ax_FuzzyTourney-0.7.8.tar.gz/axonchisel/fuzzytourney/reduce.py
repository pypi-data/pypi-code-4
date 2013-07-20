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
    def _non_nulls(self, data):
        """Return list of all non-None entries in data"""
        return [d  for d in data  if  d is not None]
    def _config_req(self, key):
        """Return param from config dict, or raise error if missing."""
        if key not in self._config:
            raise error.ConfigIncompleteError("Missing config param '{0}' in reduce '{1}'.".
                format(key, self.__class__.__name__))
        return self._config[key]


# ----------------------------------------------------------------------------


class ReduceFunction_First(ReduceFunctionBase):
    """
    Reduce function that returns first value.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        if len(data) == 0:
            return 0
        return data[0]

class ReduceFunction_Zero(ReduceFunctionBase):
    """
    Reduce function that returns 0, disregarding all values.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        return 0

class ReduceFunction_Ignore(ReduceFunction_Zero):
    """
    Reduce function that ignores all data, returning 0.
    """
    pass

class ReduceFunction_Count(ReduceFunctionBase):
    """
    Reduce function that returns count of items, including nulls.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        return len(data)

class ReduceFunction_CountNull(ReduceFunctionBase):
    """
    Reduce function that returns count of null items.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data_nulls = [d  for d in data  if  d is None]
        return len(data_nulls)

class ReduceFunction_CountNotNull(ReduceFunctionBase):
    """
    Reduce function that returns count of non-null items.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data = self._non_nulls(data)
        return len(data)

class ReduceFunction_Sum(ReduceFunctionBase):
    """
    Return sum of all numeric values.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data = self._non_nulls(data)
        if len(data) == 0:
            return 0
        return sum(data)

class ReduceFunction_Min(ReduceFunctionBase):
    """
    Return lowest numeric value.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data = self._non_nulls(data)
        if len(data) == 0:
            return 0
        return min(data)
            
class ReduceFunction_Max(ReduceFunctionBase):
    """
    Return highest numeric value.
    """
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data = self._non_nulls(data)
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
        data = self._non_nulls(data)
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
        data = self._non_nulls(data)
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
        data = self._non_nulls(data)
        if len(data) == 0:
            return 0
        mean = sum(data) / float(len(data))
        dists_sq = [(d - mean)**2 for d in data]
        avg_dists_sq = sum(dists_sq) / len(dists_sq)
        stddev = math.sqrt(avg_dists_sq)
        return stddev

class ReduceFunction_MaxChangeRate(ReduceFunctionBase):
    """
    Compares each numeric item to previous non-null, resulting in [0..1]:
        0 = no change
        0.5 = double/half
        1.0 = change to/from 0 or beyond or large relative change
        >1.0 = not possible
    Always positive result and does not consider direction of change.
    All sign reversals are considered as max change (1.0).
    Returns largest change amount of all comparisons.
    Config example: { "filter": "inc" }
    Optional config "filter" can be "all", "inc", or "dec" to only consider
    changes in any, positive, or negative direction.
    """
    def __init__(self, config):
        ReduceFunctionBase.__init__(self, config)
        self._filter = config.get('filter', 'all')
    def execute(self, data):
        """Abstract: Execute reduce func on list of data elements, returning a value."""
        data = self._non_nulls(data)
        if len(data) == 0:
            return 0
        changes = []
        prev = data[0]
        for d in data[1:]:
            ch = 0.0
            diff = d - prev
            absdiff = abs(diff)
            if absdiff > 0:
                dcmp = float(max(abs(d), abs(prev)))
                ch = 1.0
                if absdiff < dcmp:  # (not sign reversal)
                    ch = absdiff / dcmp
            prev = d
            if (self._filter == 'inc') and (diff < 0):
                continue
            if (self._filter == 'dec') and (diff > 0):
                continue
            changes.append(ch)
        if len(changes) == 0:
            return 0
        return max(changes)

