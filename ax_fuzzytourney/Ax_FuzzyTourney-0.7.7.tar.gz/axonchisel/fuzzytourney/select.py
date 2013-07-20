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
    Config example: { "n": 3, "sort": "desc", "criteria": ["score_1"] }
    If multiple criteria are specified, they are summed for purposes of
    comparison.
    """
    def __init__(self, config):
        SelectFunctionBase.__init__(self, config)
        self._competitors = []
        self._n = self._config_req('n')
        self._sort = self._config_req('sort')
        self._criteria_ids = self._config_req('criteria')
    def open(self, tournament, entrants):
        """Abstract: Begin handling tournament entrants."""
        SelectFunctionBase.open(self, tournament, entrants)
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Take results for single entrant."""
        self._competitors.append([entrant_num, entrant, criteria, lens_data])
    def close(self):
        """Abstract: Close handling tournament entrants."""
        def sort_key(comp):
            criteria = comp[2]
            score = sum([criteria[c] for c in self._criteria_ids])
            if self._sort == 'desc':
                score = -score
            return score
        self._competitors.sort(key=sort_key)
        self._competitors = self._competitors[:self._n]
        entrants = [c[1] for c in self._competitors]
        self._tournament.output.function.open(self._tournament, entrants)
        entrant_num = 0
        for competitor in self._competitors:
            entrant_num += 1
            self._tournament.output.function.entrant(competitor[0], competitor[1], competitor[2], competitor[3])
        self._tournament.output.function.close()


