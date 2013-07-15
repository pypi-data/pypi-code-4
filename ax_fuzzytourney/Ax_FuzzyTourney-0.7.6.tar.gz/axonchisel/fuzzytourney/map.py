"""
Ax_FuzzyTourney - map functions.

The list of elements produced by a lens function (for a single competitor)
have the map function applied to each by judges using configurable heuristics
prior to being reduced and applied as scores (criteria).

This module is not intended for public use.
User maps (subclass MapFunction) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import random
import math
import time
import datetime
import calendar

import axonchisel.fuzzytourney.error as error


# ----------------------------------------------------------------------------


class MapFunction:
    """Map function superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return values."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class MapFunctionBase(MapFunction):
    """Base superclass for Map functions."""
    def __init__(self, config):
        self._config = config


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# List and Dict access

class MapFunction_Index(MapFunctionBase):
    """
    Extract a single item from a list.
    Suitable for use only with input formats that create list entrants
    (such as text_csv).
    Config example: { "index": 0 }
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._index = config['index']
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return data1[self._index]

class MapFunction_Key(MapFunctionBase):
    """
    Extract a single item from a dict.
    Suitable for use only with input formats that create dict entrants
    (such as text_csv).
    Config example: { "key": "foo" }
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._key = config['key']
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return data1[self._key]


# ----------------------------------------------------------------------------
# Math and Numbers

class MapFunction_Int(MapFunctionBase):
    """Cast data to int."""
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return int(data1)

class MapFunction_Float(MapFunctionBase):
    """Cast data to float."""
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return float(data1)

class MapFunction_Scale(MapFunctionBase):
    """
    Multiply by constant value.
    Config example: { "factor": 1000, "inverse": false }
    Optional "inverse" bool config treats factor as 1/factor.
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._factor = config['factor']
        if config.get('inverse', False):
            self._factor = 1.0 / self._factor
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        val = self._factor * data1
        return val

class MapFunction_Add(MapFunctionBase):
    """
    Add a constant value.
    Config example: { "offset": 1000 }
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._offset = config.get('offset', 0)
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        val = data1 + self._offset
        return val

class MapFunction_Power(MapFunctionBase):
    """
    Raise value to power.
    Config example: { "exp": 1000 }
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._exp = config['exp']
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        return data1 ** self._exp

class MapFunction_Log(MapFunctionBase):
    """
    Return logarithm of value.
    Config example: { "base": 10 }
    Param "base" may be a numberic base or the string "e".
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._base = config['base']
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        if self._base == "e":
            return math.log(data1)
        return math.log(data1, self._base)

class MapFunction_Round(MapFunctionBase):
    """
    Round to int in one of several modes.
    Config example: { "mode": "round" }
    Supported rounding modes: round, ceil, floor. Default round.
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._mode = config.get('mode', 'round')
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        val = data1
        if self._mode == 'round':
            val = round(val)
        elif self._mode == 'ceil':
            val = math.ceil(val)
        elif self._mode == 'floor':
            val = math.floor(val)
        else:
            raise error.ConfigValueError("Invalid Round map rounding mode '{0}'".format(self._mode))
        val = int(val)
        return val

class MapFunction_Clip(MapFunctionBase):
    """
    Simply clip values to within a range.
    Config example: { "range": [-1.0, null] }
	Either of range values may be specified as null, which will prevent
	clipping on that end.
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._range = config['range']
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return self._range_none
        # Handle out of range:
        if (self._range[0] is not None) and (data1 < self._range[0]):
            return self._range[0]
        elif (self._range[1] is not None) and (data1 > self._range[1]):
            return self._range[1]
        return data1

class MapFunction_Clip2(MapFunctionBase):
    """
    Advanced clip and weight-adjust values.
    Final score flexible depending on if value is inside or outside of domain,
    with outside values clipped and inside values calculated with 
    multiplier (weight) and offset (base) applied directly to value itself. 
    Config example: {
    	"domain": [-1.0, null],
    	"range": {
    		"in": { "base": 0, "weight": -100.0 },
    		"out": { "below": 0.0, "above": 0.0 },
    		"none": 0.0
    	}
	}
	Either of domain values may be specified as null, which will prevent
	clipping on that end.
	Range "in" may be left out in which case default base 0.0, weight 1.0 are used.
	Range "none" may be left out in which case default 0.0 is used.
	Range "out" may be left out in which case default domain is used.
	if all of range is left out, behavior is similar to regular "Clip" func.
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._domain = config['domain']
        range = config.get('range')
        if not range:
            range = {}
        self._range_in = range.get('in', None)
        self._range_out = range.get('out', None)
        self._range_none = range.get('none', None)
        if self._range_in is None:
            self._range_in = {"base": 0.0, "weight": 1.0}
        if self._range_out is None:
            self._range_out = {"below": self._domain[0], "above": self._domain[1] }
        if self._range_none is None:
            self._range_none = 0.0
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return self._range_none
        # Handle out of domain:
        if (self._domain[0] is not None) and (data1 < self._domain[0]):
            return self._range_out['below']
        elif (self._domain[1] is not None) and (data1 > self._domain[1]):
            return self._range_out['above']
        # Return weighted clipped sign adjusted value:
        return self._range_in['base'] + self._range_in['weight'] * data1

class MapFunction_SignClipAdjust(MapFunctionBase):
    """
    Adjust sign and optionally clip.
    Config example: { "mode": "neg" }
    Supported modes: 
     "pos" - clip <0 to 0
     "neg" - clip >0 to 0
     "abs" - absolute value
     "all" - no adjust
    """
    def __init__(self, config):
        MapFunctionBase.__init__(self, config)
        self._mode = config['mode']
		
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        if data1 is None:
            return None
        # Adjust sign:
        if (self._mode == 'neg'):
            data1 = data1 if (data1 < 0) else 0
        elif (self._mode == 'pos'):
            data1 = data1 if (data1 > 0) else 0
        elif (self._mode == 'abs'):
            data1 = abs(data1)
        elif (self._mode == 'all'):
            data1 = data1
        else:
            raise error.ConfigValueError("Invalid SignClipAdjust map mode '{0}'".format(self._mode))
        return data1


# ----------------------------------------------------------------------------
# Date and Time

class MapFunction_DateTime_to_Time_t(MapFunctionBase):
    """
    Converts Python datetime obj to time_t seconds.
    """
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return calendar.timegm(data1.utctimetuple())

class MapFunction_Time_t_to_DateTime(MapFunctionBase):
    """
    Converts time_t seconds to Python datetime obj (UTC).
    """
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        return datetime.datetime.utcfromtimestamp(data1)

class MapFunction_DateTime_DaysFromNow(MapFunctionBase):
    """
    Given Python datetime obj (UTC), return number of days (float) from now.
    Positive indicates future, negative indicates past.
    """
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        now = datetime.datetime.utcnow()
        td = data1 - now
        secs = td.seconds + td.days * (24 * 3600)
        return float(secs) / (24 * 3600)

class MapFunction_Time_t_SecondsFromNow(MapFunctionBase):
    """
    Given int time_t, return number of seconds (int) from now.
    Positive indicates future, negative indicates past.
    """
    def execute(self, data1):
        """Abstract: Execute map func on one data element, and return value."""
        now = int(time.time())
        ttd = data1 - now
        return ttd

