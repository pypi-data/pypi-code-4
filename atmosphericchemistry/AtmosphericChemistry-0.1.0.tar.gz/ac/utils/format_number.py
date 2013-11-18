"""Format_number nicely"""

import numpy as np
from ac import tiny

def format_number(x, always_float=False, edecimals=3):
    """Format a number.
    Integers should be printed as integers, large or very small float numbers
    as exponentials. If always_float is True, integers will also get a decimal
    point. Edecimals determines the number of decimals for exponential numbers."""
    res = "%f" % (x)
    if np.abs(x) >= 1.e6 or (np.abs(x) < 1.e-4 and np.abs(x) > tiny):
        fmt = "%%.%ie" % (edecimals)
        res = fmt % (x)
    # determine number of necessary decimals
    else:
        for i, factor in enumerate([1.,10.,100.,1000.,10000.]):
            if np.abs(factor*x-np.round(factor*x)) < factor*1.e-8:
                fmt = "%%.%1if" % (i)
                res = fmt % (x)
                break
    if always_float and not "." in res:
        res += "."
    return res

