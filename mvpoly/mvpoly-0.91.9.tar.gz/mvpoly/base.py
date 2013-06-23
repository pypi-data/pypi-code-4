# -*- coding: utf-8 -*-
import numpy as np
import mvpoly.util.common

class MVPoly(object) :
    """
    Base (new-style) class for MVPoly. 
    """

    def __init__(self, dtype = float) :
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

    def maxmodnd(self, epsilon = 1e-12, verbose = False, i0 = None) :
        """
        The maximum modulus of a complex *n*-variate polynomial on 
        the unit *n*-polydisc is estimated using a method of repeated 
        subdivision of :math:`[0,2\pi]^n` and rejection of non-maximizing 
        *n*-cubes. 

        The rejection criterion is based on a lemma of S.B. Stečkin,
        extended to *n*-variate polynomials by G. De La Chevrotière [#DLC]_.

        :param epsilon: relative precision required
        :type epsilon: float
        :param verbose: set run-time information 
        :type verbose: bool
        :param i0: initial number of intervals
        :type i0: a vector of integers
        :rtype: a tuple (*M*, *t*, *h*, *evals*) 

        Here  *M* is the estimate of the maximum modulus;
        *t* is an *n*-column matrix whose rows are the midpoints of 
        non-rejected *n*-cubes; *h* is the half-width 
        of non-rejected *n*-cubes; *evals* is the total number of 
        evaluations of the polynomial used.

        .. [#DLC]
            G. De La Chevrotière. *Finding the maximum modulus of a
            polynomial on the polydisk using a generalization of 
            Stečkin's lemma*, SIAM Undergrad. Res. Online, 2, 2009.
        """
        raise NotImplementedError

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
