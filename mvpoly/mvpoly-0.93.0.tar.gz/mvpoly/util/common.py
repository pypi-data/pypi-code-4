import numpy as np

def kronn(b, c, *args) :
    """
    A version of :func:`numpy.kron` which takes an arbitrary 
    number of arguments.
    """
    a = np.kron(b, c)
    for d in args :
        a = np.kron(a, d)
    return a

def max_or_default(iterable, default) :
    """
    Like :func:`max`, but returns a default value if the
    iterable is empty.
    """
    try :
        return max(iterable)
    except ValueError :
        return default
