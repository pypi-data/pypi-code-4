"""

.. class:: MVPolyCube
   :synopsis: Multivariate polynomial class whose 
   coefficient representation is an ND-array

.. moduleauthor:: J.J. Green <j.j.green@gmx.co.uk>

"""

import mvpoly.base
import mvpoly.util.cube

import numbers
import numpy as np

class MVPolyCube(mvpoly.base.MVPoly) :
    """
    Return an object of class :class:`MVPolyCube` with
    the coefficient array set to the optional *coef*
    argument, a :class:`numpy.ndarray`.
    """
    def __init__(self, coef = None, **kwd):
        if coef is None :
            coef = []
        super(MVPolyCube, self).__init__(**kwd)
        self._coef = np.array(coef, dtype = self.dtype)

    @classmethod
    def monomials(self, n, **kwd) :
        """
        Return a *n*-tuple of each of the monomials (*x*, *y*, ..) 
        of an *n*-variate system.
        """
        return [self.monomial(i, n, **kwd) for i in range(n)]

    @classmethod
    def monomial(self, i, n, **kwd) :
        """
        Return the *i*-th monomial of an *n*-variate system,
        (*i* = 0, ..., *n*-1).
        """
        shp = tuple((1 if j==i else 0) for j in range(n))
        m = np.zeros([s+1 for s in shp])
        m.itemset(shp, 1)
        return MVPolyCube(m, **kwd)

    @classmethod
    def zero(self, **kwd) :
        """
        Return the zero polynomial.
        """
        return MVPolyCube(**kwd)

    def dtype_set_callback(self, value) :
        """
        For internal use. Sets the datatype of the 
        coefficient array.
        """
        self.coef.dtype = np.dtype(value)

    @property
    def coef(self) :
        return self._coef

    @coef.setter
    def coef(self, value) :
        self._coef = value

    def __setitem__(self, key, value) :
        """
        The setter method, delegated to the *coef* attribute.
        """
        self.coef[key] = value

    def __getitem__(self, key) :
        """
        The getter method, delegated to the *coef* attribute.
        """
        return self.coef[key]

    def __add__(self, other) :
        """
        Add an :class:`MVPolyCube` to another, or to a :class:`numpy.ndarray`,
        or to a number; return an :class:`MVPolyCube`.
        """
        a = self.coef
        if isinstance(other, MVPolyCube) :
            b = other.coef
        elif isinstance(other, list) :
            b = np.array(other)
        elif isinstance(other, numbers.Number) :
            b = np.array([other])
        else :
            raise TypeError, "cannot add MVPolyCube to %s" % type(other)
        return MVPolyCube(mvpoly.util.cube.padded_sum(a, b), 
                          dtype = self.dtype)

    def __radd__(self, other) :
        """
        As add, but with the types in the opposite order -- this is
        routed to add.
        """
        return self.__add__(other)

    def __mul__(self, other) :
        """
        Convolve our coefficient array with that of *other*
        and return an :class:`MVPolyCube` object initialised with
        the result.
        """
        if isinstance(other, MVPolyCube) :
            return MVPolyCube(mvpoly.util.cube.convn(self.coef, other.coef),
                              dtype = self.dtype)
        elif isinstance(other, numbers.Number) :
            return MVPolyCube(self.coef * other, dtype = self.dtype)
        else :
            raise TypeError, \
                "cannot multiply MVPolyCube by %s" % type(other)

    def __rmul__(self, other) :
        """
        Reverse order multiply, as add
        """
        return self.__mul__(other)

    def __neg__(self) :
        """
        Negation of a polynomial, return the polynomial with negated 
        coefficients.
        """
        return MVPolyCube(-(self.coef), dtype = self.dtype)

    def __eq__(self, other) :
        """
        Equality of polynomials. 
        """
        return ((self - other).coef == 0).all()

    def order(self) :
        """
        Return the maximal order of each of the variables of
        the polynomial as a tuple of integers. For the zero 
        polynomial, returns the empty tuple.
        """
        if self.coef.any() :
            return tuple(n-1 for n in self.coef.shape) 
        else :
            return ()

    def homdeg(self) :
        """
        The *homogeneous degree*, the maximal sum of the
        monomial degrees of monomials with nonzero coefficients. 
        """
        nzis = np.nonzero(self.coef)
        degs = [sum(t) for t in zip(*nzis)]
        if not degs :
            raise ValueError("homogeneous degree undefined for zero polynomial")
        return np.max(degs)

    def eval(self, *args) :
        """
        Evaluate the polynomial at the points given by *args*.
        There should be as many arguments as the polynomial 
        has variables.  The argument can be numbers, or arrays
        (all of the same shape).
        """
        return mvpoly.util.cube.horner(self.coef, self.dtype, *args)

    def compose(self, *args) :
        """
        Compose polynomials. The arguments, which should be
        :class:`MVPolyCube` polynomials, are substituted 
        into the corresponding variables of the polynomial.
        """

        # Note that this could be moved into the base class
        # if we were to insist that each subclass had a 
        # method enumerating the monomial indices and the
        # corresponding non-zero coeficients, probably

        dims = self.coef.shape
        N = len(dims)

        if N != len(args) :
            msg = "wrong number of args (%i) for a %i-variable polynomial" % \
                (len(args), N)
            raise(ValueError, msg)
        C = self.coef.flat

        # generate list-of-list of powers of monomials

        X = [0] * N
        for i in range(N) :
            order = dims[i] - 1
            if not order > 0 :
                continue
            Xi = [0] * order
            Xi0 = args[i]
            Xi[0] = Xi0
            for n in range(1, order) :
                Xi[n] = Xi[n-1] * Xi0
            X[i] = Xi

        # iterate through coefficients of p, accumulating
        # the monomials in the output q

        q = MVPolyCube([0], dtype=self.dtype)  

        for i in range(np.prod(dims)) :
            if C[i] == 0 :
                continue
            M = MVPolyCube([1], dtype=self.dtype)  
            idx = np.unravel_index(i, dims)
            for j in range(len(idx)) :
                n = idx[j] - 1
                if n >= 0 :
                    M = M * X[j][n]
            q += C[i] * M

        return q  

    def diff(self, *args) :
        """
        Differentiate polynomial. The integer arguments
        should indicate the number to times to differentiate
        with respect to the corresponding polynomial variable,
        hence ``p.diff(0,1,1)`` would correspond to 
        :math:`\partial^2 p / \partial y \partial z`.
        """
        return MVPolyCube(mvpoly.util.cube.diff(self.coef, args),
                          dtype = self.dtype)  

    def int(self, *args, **kwargs) :
        """
        Indefinite integral of polynomial. The arguments are
        as for :meth:`diff`, but an optional *dtype* keyword 
        argument can be appended to specify the *dtype* of the
        output polynomial.
        """
        dtype = np.dtype(kwargs.get('dtype', self.dtype))
        return MVPolyCube(mvpoly.util.cube.int(self.coef, args, dtype), 
                          dtype=dtype)

    def maxmodnb(self, **kwargs) :
        """
        Maximum modulus of the polynomial on the unit ball, this
        method is only available if the :mod:`maxmodnb` package
        is installed (and that is in an early stage of development).
        """
        return mvpoly.util.cube.maxmodnb(self.coef, **kwargs)
