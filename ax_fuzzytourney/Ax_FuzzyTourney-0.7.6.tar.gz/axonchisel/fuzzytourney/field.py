"""
Ax_FuzzyTourney - output field functions.

Output field functions operate on entrants to produce lists of data for output.

This module is not intended for public use.
User field functions (subclass OutputField) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import sys
import math
import random

import axonchisel.fuzzytourney.error as error


# ----------------------------------------------------------------------------


class OutputFieldFunction(object):
    """Output field function superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def setup(self, tournament, entrants):
        """Perform initial setup for tournament."""
        raise NotImplementedError()
    def ids(self):
        """Abstract: Return list of ids for fields."""
        raise NotImplementedError()
    def names(self):
        """Abstract: Return list of display names for fields."""
        raise NotImplementedError()
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class OutputFieldFunctionBase(OutputFieldFunction):
    """
    Base superclass for output fields.
    Allows optional specification of id and name in config,
    which otherwise are dynamically determined from class name.
    Config example: {
        "id": 'my_field',
        "name": "My field"
        "format": "{0:0.3f}"
    }
    Optional "format" is used to format value as string via .format().
    See http://docs.python.org/2/library/string.html#formatspec
    """
    CLS_PREFIX = 'OutputFieldFunction_'
    def __init__(self, config):
        self._config = config
        self._tournament = None
        self._entrants = None
        self._id = config.get('id', type(self).__name__[len(self.CLS_PREFIX):])
        self._name = config.get('name', self._id.replace("_", " "))
        self._formatspec = config.get('format', None)
    def setup(self, tournament, entrants):
        """Perform initial setup for tournament."""
        self._tournament = tournament
        self._entrants = entrants
    def ids(self):
        """Abstract: Return list of ids for fields."""
        return [self._id]
    def names(self):
        """Abstract: Return list of display names for fields."""
        return [self._name]
    def _format(self, val):
        if self._formatspec is not None:
            fmtspec = self._formatspec
            return fmtspec.format(val)
        return val

class OutputFieldFunctionBaseCount(OutputFieldFunctionBase):
    """
    Base superclass for output fields that take "count" config
    and product that many fields.
    Config example: { ...
        "count": 5
    ... }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._count = config.get('count', None)
    def ids(self):
        """Abstract: Return list of ids for fields."""
        return self._multiple_ids(self._count)
    def names(self):
        """Abstract: Return list of display names for fields."""
        return self._multiple_names(self._count)
        self._count = config['count']
    def _multiple_ids(self, count):
        return ['{0}_{1}'.format(self._id, i+1) for i in range(count)]
    def _multiple_names(self, count):
        return ['{0} {1}'.format(self._name, i+1) for i in range(count)]


# ----------------------------------------------------------------------------


class OutputFieldFunction_Counter(OutputFieldFunctionBase):
    """
    Output field as incrementing counter.
    Config example: { "start": 1, "inc": 1 }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._start = config.get('start', 0)
        self._inc = config.get('inc', 1)
        self._val = self._start
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        v = self._val
        self._val += self._inc
        return [self._format(v)]

class OutputFieldFunction_Entrant_Num(OutputFieldFunctionBase):
    """
    Output field to show entrant num.
    Config example: { "lpad": 3 }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._lpad = config.get('lpad', 0)
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        if self._lpad:
            fstr = "{0:%dd}" % int(self._lpad)
            return [self._format(fstr.format(entrant_num))]
        else:
            return [self._format(entrant_num)]

class OutputFieldFunction_Entrant(OutputFieldFunctionBase):
    """Output field to show entrant."""
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(entrant)]

class OutputFieldFunction_Entrant_Index(OutputFieldFunctionBase):
    """
    Output field to show item from entrant that is list struct.
    Config example: { "index": 0 }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._index = config['index']
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(entrant[self._index])]

class OutputFieldFunction_Entrant_Key(OutputFieldFunctionBase):
    """
    Output field to show item from entrant that is dict struct.
    Config example: { "key": "foo" }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._key = config['key']
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(entrant[self._key])]

class OutputFieldFunction_Progress(OutputFieldFunctionBase):
    """Output field to show percentage through all entrants."""
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._val = 0
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        self._val += 1
        prog = round(float(self._val) / len(self._entrants) * 100.0)
        return [self._format("{0:3.0f}%".format(prog))]

class OutputFieldFunction_Criterion(OutputFieldFunctionBase):
    """
    Output field to show specific calculated criterion.
    Config example: { "criterion": "score_1" }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._criterion_id = config['criterion']
    def ids(self):
        """Abstract: Return list of ids for fields."""
        return [self._criterion_id]
    def names(self):
        """Abstract: Return list of display names for fields."""
        c = self._tournament.criteria.get_by_id(self._criterion_id)
        if not c:
            raise error.ConfigValueError("Invalid criteria id '{0}' in criterion field".format(self._criterion_id))
        return ['{0}'.format(c.name)]
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        val = criteria[self._criterion_id]
        return [self._format(val)]

class OutputFieldFunction_Lens_Datum(OutputFieldFunctionBase):
    """
    Output field to show specific calculated lens datum.
    Config example: { "lens_id": "lens_first", "lens_index": 0 }
    """
    def __init__(self, config):
        OutputFieldFunctionBase.__init__(self, config)
        self._lens_id = config['lens_id']
        self._lens_index = config['lens_index']
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(lens_data[self._lens_id][self._lens_index])]

class OutputFieldFunction_Lens_Data(OutputFieldFunctionBaseCount):
    """
    Output field to show multiple fields of calculated lens data.
    Config example: { "lens_id": "lens_first", "lens_indices": [0, 2, 3, 6] }
    """
    def __init__(self, config):
        OutputFieldFunctionBaseCount.__init__(self, config)
        self._lens_id = config['lens_id']
        self._lens_indices = config['lens_indices']
        self._count = len(self._lens_indices)
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(lens_data[self._lens_id][i]) for i in self._lens_indices]

class OutputFieldFunction_Rand(OutputFieldFunctionBaseCount):
    """
    Output field to produce a list of random numbers, mostly for testing.
    Config example: { "count": 3 }
    """
    def __init__(self, config):
        OutputFieldFunctionBaseCount.__init__(self, config)
    def execute(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Execute field func on one entrant, and return values."""
        return [self._format(random.random() for x in range(self._count))]


