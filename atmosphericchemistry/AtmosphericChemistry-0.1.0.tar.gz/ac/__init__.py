"""AtmosphericChemistry Package"""

__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '0.1.0'
__date__ = '2013-10-31'
__license__ = 'MIT'


import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

__all__ = [ "gasphase", "utils" ]

# define threshold values
import numpy as np
tiny = np.finfo(float).tiny
eps = np.finfo(float).eps

# set directory with test data sets
import os
TESTDATADIR = os.path.dirname(__file__)+"/testdata"

