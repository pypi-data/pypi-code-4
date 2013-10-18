import numpy as np
import scipy.signal
import mvpoly.util.common
import warnings

def int(p, d, dtype) :
    """
    Integrate the multivatiate polynomial whose coefficients
    are given by the :class:`numpy.array` argument *p* and as 
    many times as given by the non-negative tuple *d*. The 
    final argument, *dtype*, specifies the data-type of the 
    output; if this is an integer type then the results may
    be incorrect (due to integer division) so a warning will
    be issued.
    """

    if np.dtype(dtype).kind in set(['i', 'u']) :
        msg = "integral output of type %s" % (np.dtype(dtype).name)
        warnings.warn(msg, RuntimeWarning)

    pv = p.shape
    pn = len(pv)

    assert pn == len(d), \
        "wrong number of args (%i) for a %i-variable polynomial" % \
        (len(d), pn)

    def int2(p, k, dtype) :
        pv = p.shape
        pn = len(pv)
        qv = tuple([pv[i] + (1 if i == k else 0) for i in range(pn)])
        q = np.zeros(qv, dtype=dtype)
        idx = tuple([slice(None) for i in range(0, k)] +
                    [slice(1, pv[k]+1)] + 
                    [slice(None) for i in range(k+1, pn)])
        q[idx] = p / meshgridn(pv, k, 
                               np.array(range(1, pv[k]+1), dtype=dtype))
        return q

    q = p.copy()

    for k in range(pn) :
        for _ in range(d[k]) :
            q = int2(q, k, dtype)

    return q


def diff(p, d) :
    """
    Differentiate the multivatiate polynomial whose coefficients
    are given by the :class:`numpy.array` argument *p* and as 
    many times as given by the non-negative tuple *d*.
    """
    pv = p.shape
    pn = len(pv)

    assert pn == len(d), \
        "wrong number of args (%i) for a %i-variable polynomial" % \
        (len(d), pn)

    def diff2(p, k) :
        """
        Differentiate once in the *k*-th variable.
        """
        pv = p.shape
        pn = len(pv)
        idx = tuple([slice(None) for _ in range(0, k)] +
                    [slice(1, pv[k])] + 
                    [slice(None) for _ in range(k+1, pn)])
        q  = p[idx]
        qv = q.shape
        r  = meshgridn(qv, k, np.array(range(1, qv[k]+1), dtype=p.dtype))
        return r*q

    q = p.copy()

    for k in range(pn) :
        if d[k] > pv[k] :
            return np.array([0])
        for _ in range(d[k]) :
            q = diff2(q, k)

    return q

def meshgridn(shp, n, v) :
    """
    Given a shape tuple *shp = (s1, s2, ... sm)*, a 
    specified dimension *n* and a vector *v* with *sn* elements,
    this function returns a :class:`numpy.ndarry` which has
    *v* replicated in the *n*-th dimension.  Thus it it rather 
    like the *n*-th return value of :func:`numpy.meshgrid`, but 
    without constructing the other return values.
    """
    assert shp[n] == len(v), "bad meshgrid arguments %s %s" % \
        (repr(shp), repr(v))

    dt = v.dtype
    nd = len(shp)

    if nd == 1 :
        return v

    args = tuple( \
        [ np.ones(shp[i], dtype=dt) for i in range(n) ] + [ v ] + \
        [ np.ones(shp[i], dtype=dt) for i in range(n+1, nd) ] )

    val = mvpoly.util.common.kronn(*args)
    val.shape = shp

    return val

def padded_sum(*args) :
    """
    Add the :class:`numpy.ndarry` arguments which may be of 
    differing dimensions and sizes, return a :class:`numpy.ndarray`.
    This code is largely based on this Bi Rico's answer to this 
    `Stack Exchange question <http://stackoverflow.com/questions/16180681>`_.
    """
    n = max(a.ndim for a in args)
    dt = args[0].dtype
    args = [a.reshape((n - a.ndim)*(1,) + a.shape) for a in args]
    shp = np.max([a.shape for a in args], 0)
    res = np.zeros(shp, dtype=dt)
    for a in args:
        idx = tuple(slice(i) for i in a.shape)
        res[idx] += a
    return res

def convn(a, b) :
    """
    Convolve :class:`numpy.ndarry` arguments *a* and *b*, and
    return the :class:`numpy.ndarry` that results.    
    """
    sa, sb = (x.shape for x in (a, b))
    if len(sa) < len(sb) :
        a.shape = dimension_pad(sa, len(sb))
    elif len(sa) > len(sb) :
        b.shape = dimension_pad(sb, len(sa))
    return scipy.signal.convolve(a, b)

def dimension_pad(S, n) :
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
            p0 = np.squeeze(p[i, :])
            p1[(i,) + c] = horner_recurse(p0, vp[1:], nvp-1, x[1:, :])
        return horner_nd(p1, vp[0], x[0, :])

    def coerce_np_array(arg) :
        return np.array([arg] if np.isscalar(arg) else arg)

    args = [coerce_np_array(arg) for arg in args]

    shp = args[0].shape
    assert all(shp == s for s in (arg.shape for arg in args)), \
        "Horner: all argument should be same shape"

    dp = p.shape
    nvp = len(dp)

    udims, ndims = [], []
    for i in range(nvp) :
        (udims, ndims)[dp[i] == 1].append(i)

    if len(ndims) > 0 :
        p = np.squeeze(p, axis=ndims)
        args = [args[i] for i in udims]
        dp = p.shape
        nvp = len(dp)

    if shp :
        dx = (nvp,) + shp
        x = np.zeros(dx, dtype=dtype)
        c = tuple(None for i in range(nvp))
        for i in range(nvp) :
            x[(i,) + c] = args[i]
        x.shape = (dx[0], -1)
        y = horner_recurse(p, dp, nvp, x)
        y.shape = dx[1:]

    else :
        x = np.array(args)
        y = horner_recurse(p, dp, nvp, x)

    if y.size > 1 :
        return y
    else :
        return y.flat[0]

def maxmodnb(p, **kwargs) :
    """
    Return the maximum modulus of the polynomial whose
    coefficients are given by the array *p*. Requires the
    :mod:`maxmodnb` package (not yet released).
    """
    return __import__("maxmodnb").maxmodnb(p, **kwargs)
