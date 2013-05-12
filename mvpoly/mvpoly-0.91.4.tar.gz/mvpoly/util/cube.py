import numpy as np
import scipy.signal

def padded_sum(*args):
    """
    Add the :class:`numpy.ndarry` arguments which may be of 
    differing dimensions and sizes, return a :class:`numpy.ndarray`.
    This code is largely based on this Bi Rico's answer to this 
    `Stack Exchange question <http://stackoverflow.com/questions/16180681>`_.
    """
    n = max(a.ndim for a in args)
    args = [a.reshape((n - a.ndim)*(1,) + a.shape) for a in args]
    shp = np.max([a.shape for a in args], 0)
    res = np.zeros(shp)
    for a in args:
        idx = tuple(slice(i) for i in a.shape)
        res[idx] += a
    return res

def convn(A, B) :
    """
    Convolve :class:`numpy.ndarry` arguments *A* and *B*, and
    return the :class:`numpy.ndarry` that results.    
    """
    sA, sB = (x.shape for x in (A,B))
    if len(sA) < len(sB) :
        A.shape = _dimension_pad(sA, len(sB))
    elif len(sA) > len(sB) :
        B.shape = _dimension_pad(sB, len(sA))

    if any(x.dtype == float for x in [A, B])  :
        return scipy.signal.fftconvolve(A, B)
    else :
        return scipy.signal.convolve(A, B)

def _dimension_pad(S, n) :
    """
    Return a shape tuple extended so that it has *n*
    dimensions
    """
    return S + tuple(1 for i in range(n-len(S)))

def horner(p, dtype=float, *args) :
    """
    Evaluate polynomial with coefficients array *p* at 
    all of the points given by the equal-sized arrays 
    *args* = *X*, *Y*, ..., (as many as the dimension 
    of *p*). Returns a :class:`numpy.ndarray` of the same size.
    """

    dp = p.shape
    nvp = len(dp)
    
    if len(args) > 1 :
        da = (np.array(args[0])).shape
        for i in range(1, len(args)) :
            if (np.array(args[i])).shape != da :
                raise ValueError("Horner: all argument should be same size") 
        if not da :
            da = (1,)
        dx = (nvp,) + da
        x = np.zeros(dx, dtype=dtype)
        c = tuple(None for i in range(nvp))
        for i in range(len(args)) :
            x[(i,) + c] = args[i]
    else :
        x = args[0]
        dx = (np.array(x)).shape

    ndx = len(dx)

    if nvp != dx[0] :
        raise ValueError("size mismatch %i %i" % (nvp, dx[0]))

    def horner_1d(p, n, x) :
        y = p[n-1] * np.ones(x.shape, dtype=dtype)
        for k in range(n-1) :
            y = y * x + p[n-2-k]
        return y

    def horner_nd(p, n, x) :
        if p.ndim == 1 : 
            return horner_1d(p, n, x)
        y = p[n-1, :]
        for k in range(n-1) :
            y = y * x + p[n-2-k, :]
        return y

    def horner_recurse(p, vp, nvp, x) :
        if nvp == 1 :
            return horner_1d(p, vp[0], x)
        nel = x.shape[1]
        c1 = vp[:1] + ((nel,) if nel > 1 else ())
        p1 = np.zeros(c1, dtype=dtype)
        c = (None,) * (nvp-1)
        for i in range(vp[0]) :
            p0 = np.squeeze(p[i,:])
            p1[(i,) + c] = horner_recurse(p0, vp[1:], nvp-1, x[1:,:])
        return horner_nd(p1, vp[0], x[0,:])

    vp = dp[0:nvp]

    if ndx == 1 :
        y = horner_recurse(p, vp, nvp, x)
    else :
        x.shape = (dx[0], -1)
        y = horner_recurse(p, vp, nvp, x)
        y.shape = dx[1:]

    return y

