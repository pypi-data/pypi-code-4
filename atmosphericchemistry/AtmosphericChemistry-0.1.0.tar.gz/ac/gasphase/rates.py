# -*- coding: utf-8 -*-
"""
Rates

Python class to manage rate coefficient expressions and functions and module
functions for popular rate coefficient expressions.

Instantiation:
- c = rateCoefficient(expression)
Attributes:
- kterm : string
- ktree : mathTree representation of kterm 
Methods:
- get_
"""

import numpy as np
from ac.utils import extract_numbers
from ac.utils.mathtree import mathTree


__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-10-03'
__license__ = 'MIT'



class rateCoefficient(object):
    """handles the rate coefficient expression of gas-phase reactions.
    This includes a basic interface to store a string expression for use
    in a chemical mechanism and a more elaborate interface for evaluating
    rate coefficient expressions."""

    def __init__(self, arg=None):
        """Initialize. Arg must be string."""
        if arg is None or not arg:
            raise ValueError("Rate coefficient expression must not be None or empty!")
        if not isinstance(arg, basestring):
            raise ValueError("Rate coefficient expression must be string type!")
        self._kterm = arg
        self._tree = None


    def __repr__(self):
        return self._kterm


    def extract_coefficients(self):
        """Attempt to extract numerical coefficients from a rate coefficient expression and
        returns these as list. This is used for writing chemical mechanism files."""
        return extract_numbers(self._kterm)


    def extract_variables(self, undefined=False):
        """Return all variables of the kterm expression. If the undefined keyword is set,
        only undefined variables will be returned."""
        if self._tree is None:
            self._tree = mathTree(self._kterm)
            self._tree.resolve()
        if undefined:
            variables = [k for k, v in self._tree.variables.items() if v is None]
        else:
            variables = [k for k, v in self._tree.variables.items()]
        return variables

 
    def get_variables(self, undefined=False, ignore_T=True):
        """Return all variables of the kterm expression as dictionary. If the
        undefined keyword is set, only undefined variables will be returned."""
        if self._tree is None:
            self._tree = mathTree(self._kterm)
            self._tree.resolve()
        variables = {}
        for k, v in self._tree.variables.items():
            add_it = True
            if undefined and v is not None:
                add_it = False
            if ignore_T and k == "T":
                add_it = False
            if add_it:
                variables[k] = v
        return variables

    
# ---- Module functions ----

def ktroe(k0_300, n, kinf_300, m, fc, T=298., M=2.77e19):
    """Evaluate a Troe 3-body reaction rate coefficient"""
    k0_T = k0_300 * (300./T)**n
    kinf_T = kinf_300 * (300./T)**m
    kratio = k0_T * M / kinf_T
    kfexp = 1./(1. + np.log10(kratio)**2)
    k = k0_T*M/(1.+kratio) * fc**kfexp
    return k

def kactivation(k0_300, n, kinf_300, m, fc, T=298., M=2.77e19):
    """Evaluate an 'activation' 3-body reaction rate coefficient
    This formula is very similar to ktroe, but mind the M.
    It is used for the CO+OH reaction according to JPL(2011)."""
    k0_T = k0_300 * (300./T)**n
    kinf_T = kinf_300 * (300./T)**m
    kratio = k0_T * M / kinf_T
    kfexp = 1./(1. + np.log10(kratio)**2)
    k = k0_T/(1.+kratio) * fc**kfexp
    return k
