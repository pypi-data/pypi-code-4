# -*- coding: utf-8 -*-
import numpy as np
import mvpoly.util.common

class MVPoly(object) :
    """
    Base (new-style) class for MVPoly. 
    """
    def __init__(self, dtype = np.double) :
        self._dtype = dtype 

    # subclasses are encouraged to overide the method
    # dtype_set_callback(value) below, it can set the
    # the datatype of the representation.

    def dtype_set_callback(self, value) :
        """
        For internal use. Do-nothing base-class default 
        callback for setting the dtype. 
        """
        pass

    @property
    def dtype(self) :
        return self._dtype

    @dtype.setter
    def dtype(self, value) :
        self.dtype_set_callback(value)
        self._dtype = value

    def intd(self, *intervals) :
        """
        Evaluate the definite integral over the cube determined 
        by the *intervals*.
        """
        pv = self.order()
        pn = len(pv)
        assert len(intervals) == pn, \
            "%i variables but %i intervals" % (pn, len(intervals))

        ip = self.int(*(tuple([1]*pn)))
        lims = np.array(intervals)

        v = lims[0, :]
        for i in range(1, pn) :
            v = np.vstack((np.tile(v, (1, 2)), 
                           np.kron(lims[i, :], np.ones((1, 2**i)))))

        if pn == 1 :
            sgn = [-1, 1]
        else :
            c = tuple([-1, 1] for i in range(pn))
            sgn = mvpoly.util.common.kronn(*c)

        if pn > 1 :
            v = [v[i, :] for i in range(pn)]
            w = ip.eval(*v)
        else :
            w = ip.eval(v)

        return np.dot(sgn, w)

    def maxmodnd(self, epsilon = 1e-12, i0 = None) :
        """
        The maximum modulus of a complex *n*-variate polynomial on 
        the unit *n*-polydisc is estimated using a method of repeated 
        subdivision of :math:`[0,2\pi]^n` and rejection of non-maximizing 
        *n*-cubes. 

        The rejection criterion is based on a lemma of S.B. Stečkin,
        extended to *n*-variate polynomials by G. De La Chevrotière [#DLC]_.

        :param epsilon: relative precision required
        :type epsilon: float
        :param i0: initial number of intervals in each dimension
        :type i0: an *n*-vector of integers
        :rtype: a tuple (*M*, *t*, *h*, *evals*) 

        Here  *M* is the estimate of the maximum modulus;
        *t* is an *n*-row matrix whose columns are the midpoints of 
        non-rejected *n*-cubes; *h* is the half-width 
        of non-rejected *n*-cubes; *evals* is the total number of 
        evaluations of the polynomial used.

        .. [#DLC]
            G. De La Chevrotière. *Finding the maximum modulus of a
            polynomial on the polydisk using a generalization of 
            Stečkin's lemma*, SIAM Undergrad. Res. Online, 2, 2009.
        """

        def initial_workspace(i0, n, h) :
            t0 = np.arange(i0, dtype=float).reshape((1, i0))
            t  = t0.copy()
            for k in range(1, n) :
                a = np.tile(t, (1, i0))
                b = np.kron(t0, np.ones((1, i0**k), dtype=float))
                t = np.vstack((a, b))
            return 2*h*t + h

        def subdivide_workspace(t, n, h) :
            m = t.shape[1]
            t = np.tile(t, (1, 2**n))
            for k in range(n) :
                a = np.kron([h, -h], np.ones((1, m*2**k)))
                b = np.tile(a, (1, 2**(n-k-1)))
                t[np.r_[k, :]] += b
            return t

        # parameters
        d  = self.order()
        n  = len(d)
        hd = self.homdeg()
        if i0 is None :
            i0 = 3*hd
        assert i0 > 2*hd, "i0 must be at least twice the polynomial degree"

        # starting values
        h = np.pi / i0
        evals = 0
        M2min = 0.0
        M2max = np.inf

        t = initial_workspace(i0, n, h)

        while True :

            # evaluate polynomial
            z = np.exp(t * 1j)            
            pz = self.eval(*(z[i, :] for i in range(n)))
            qz = np.real(pz)**2 + np.imag(pz)**2

            # statistics
            eval0 = qz.size
            evals += eval0

            # evaluate bounds
            M2min = max(M2min, np.max(qz))
            SC    = np.cos(hd*h)
            M2max = M2min/SC

            # check for termination
            if M2max - M2min < 4*epsilon*M2min :
                break

            # rejection
            rT  = M2min * SC
            ind = np.nonzero(qz > rT)[0]
            t   = t[:, ind]

            # subdivision
            h /= 2
            t = subdivide_workspace(t, n, h)

        M = np.sqrt((M2min + M2max)/2)

        return (M, t, h, evals)

    def _binary_pow(self, n) :
        """
        Integer power implemented by binary division.
        """
        p = self
        if n == 1 :
            return p
        if n % 2 == 0 :
            p = p._binary_pow(n/2)
            return p * p
        else :
            return p * p._binary_pow(n-1)

    def __pow__(self, n) :
        """
        Default integer power, subclasses may choose to implement a 
        more efficient method (FFT and so on) for their particular 
        data-representation.
        """
        if not isinstance(n, int) :
            raise TypeError, "bad power exponent type"
        if n < 0 :
            raise ArithmeticError, "cannot handle negative integer powers"
        if n == 0 :
            return self.__init__(1, dtype = self.dtype)

        return self._binary_pow(n)

    def __sub__(self, other) :
        """
        Subtraction implemented with add and negate.
        """
        return self + (-other)

    def __rsub__(self, other) :
        """
        Subtraction with reversed arguments.
        """
        return other + (-self)

    def __call__(self, *args) :
        """
        Evaluate or compose polynomials, depending on whether
        any of the arguments are of :class:`MVPoly` class.
        """
        if any(isinstance(arg, self.__class__) for arg in args) :
            return self.compose(*args)
        else :
            return self.eval(*args)
