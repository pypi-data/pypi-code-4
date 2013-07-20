"""
Ax_FuzzyTourney - select functions.

Used to capture processed entrants from tournament, manipulate,
and feed to output.

This module is not intended for public use.
User selects (subclass SelectFunction) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import sys
import random


# ----------------------------------------------------------------------------


class SelectFunction(object):
    """Select function superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def open(self, tournament, entrants):
        """Abstract: Begin handling tournament entrants."""
        raise NotImplementedError()
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Take results for single entrant."""
        raise NotImplementedError()
    def close(self):
        """Abstract: Close handling tournament entrants."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class SelectFunctionBase(SelectFunction):
    """Base superclass for Select functions."""
    def __init__(self, config):
        self._config = config
    def open(self, tournament, entrants):
        """Abstract: Begin handling tournament entrants."""
        self._tournament = tournament
        self._entrants = entrants
    def _config_req(self, key):
        """Return param from config dict, or raise error if missing."""
        if key not in self._config:
            raise error.ConfigIncompleteError("Missing config param '{0}' in select '{1}'.".
                format(key, self.__class__.__name__))
        return self._config[key]


# ----------------------------------------------------------------------------


class SelectFunction_All(SelectFunctionBase):
    """
    Pass-through select that uses output directly.
    """
    def __init__(self, config):
        SelectFunctionBase.__init__(self, config)
    def open(self, tournament, entrants):
        """Abstract: Begin handling tournament entrants."""
        SelectFunctionBase.open(self, tournament, entrants)
        self._tournament.output.function.open(tournament, entrants)
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Take results for single entrant."""
        self._tournament.output.function.entrant(entrant_num, entrant, criteria, lens_data)
    def close(self):
        """Abstract: Close handling tournament entrants."""
        self._tournament.output.function.close()


class SelectFunction_TopNCriteria(SelectFunctionBase):
    """
    Buffers all competitors then chooses and outputs top N.
    Config example: { "n": 3, "sort": "desc", "criteria": ["score_1"], "min": 100, "max": 500 }
    If multiple criteria are specified, they are summed for purposes of
    comparison.
    Optional config params "min" and "max" may be used to filter the output
    to only show scores in range.
    """
    def __init__(self, config):
        SelectFunctionBase.__init__(self, config)
        self._competitors = []
        self._n = self._config_req('n')
        self._sort = self._config_req('sort')
        self._criteria_ids = self._config_req('criteria')
        self._min = config.get('min', None)
        self._max = config.get('max', None)
    def open(self, tournament, entrants):
        """Abstract: Begin handling tournament entrants."""
        SelectFunctionBase.open(self, tournament, entrants)
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Take results for single entrant."""
        self._competitors.append([entrant_num, entrant, criteria, lens_data])
    def close(self):
        """Abstract: Close handling tournament entrants."""
        # Filter:
        competitors = [c for c in self._competitors if self._score_in_range(c)]
        # Sort:
        competitors.sort(key=lambda c: self._sort_key(c))
        # Clip winners:
        competitors = competitors[:self._n]
        # Output:
        entrants = [c[1] for c in competitors]
        self._tournament.output.function.open(self._tournament, entrants)
        entrant_num = 0
        for competitor in competitors:
            entrant_num += 1
            self._tournament.output.function.entrant(competitor[0], competitor[1], competitor[2], competitor[3])
        self._tournament.output.function.close()
    def _comp_score(self, comp):
        """Calc competitor score based on sum of criteria requested."""
        criteria = comp[2]
        return sum([criteria[c] for c in self._criteria_ids])
    def _score_in_range(self, comp):
        """Check if competitor score is in range specified."""
        score = self._comp_score(comp)
        if (self._min is not None) and (score < self._min):
            return False
        if (self._max is not None) and (score > self._max):
            return False
        return True
    def _sort_key(self, comp):
        """Sorting function."""
        score = self._comp_score(comp)
        if self._sort == 'desc':
            score = -score
        return score



