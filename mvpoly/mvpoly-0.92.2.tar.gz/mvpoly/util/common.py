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

