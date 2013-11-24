# -*- coding: utf-8 -*-
"""

.. class:: MVPolyDict
   :synopsis: Multivariate polynomial class whose 
   coefficient representation is a dictionary

.. moduleauthor:: J.J. Green <j.j.green@gmx.co.uk>

"""

import mvpoly.base
import mvpoly.util.dict
import mvpoly.util.common

import numbers
import numpy as np
import warnings

class MVPolyDict(mvpoly.base.MVPoly) :
    """
    Return an object of class :class:`MVPolyDict` with
    the coefficient dictionary set to the optional *coef*
    argument.
    """
    def __init__(self, coef = None, **kwd):
        super(MVPolyDict, self).__init__(**kwd)
        self._coef = {} if coef is None else coef
        self.dtype_set_callback(self.dtype)
        self._vars_dirty = True


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
        m = MVPolyDictMonomial({i:1})
        d = { m.key: np.array(1) }
        return MVPolyDict(d, **kwd)

    @classmethod
    def zero(self, **kwd) :
        """
        Return the zero polynomial. 
        """
        return MVPolyDict(**kwd)


    def dtype_set_callback(self, value) :
        """
        For internal use. Sets the datatype of the 
        coefficients.
        """
        dtype = np.dtype(value)
        for k, v in self.coef.iteritems() :
            self.coef[k] = np.array(v, dtype = dtype)
            

    @property
    def numvar(self) :
        """
        Return the number of variable occuring in monomials
        of the polynomial, for :math:`2x^3 + 5xz` this would
        be two.
        """
        return len(self.vars)


    @property
    def maxvar(self) :
        """
        Return the largest (1-based) index of variables
        occuring in the monomials of the polynomial, for
        :math:`2x^3 + 5xz` this would be three.
        """
        v = self.vars
        return 0 if len(v) == 0 else max(v) + 1


    @property
    def vars(self) :
        if self._vars_dirty :
            vs = set()
            for (key, val) in self.coef.iteritems() :
                vs |= set(MVPolyDictMonomial(key = key).dict.keys())
            self._vars = vs
            self._numvar_dirty = False
        return self._vars


    @property
    def coef(self) :
        return self._coef

    @coef.setter
    def coef(self, value) :
        self._coef = value


    def __setitem__(self, index, value) :
        """
        The setter method, delegated to the *coef* attribute.
        """
        if value == 0 :
            return
        self._vars_dirty = True
        key = MVPolyDictMonomial(index = index).key
        self.coef[key] = np.array(value, self.dtype)


    def __getitem__(self, index) :
        """
        The getter method, delegated to the *coef* attribute.
        """
        key = MVPolyDictMonomial(index = index).key
        return self.coef.get(key, np.array(0, self.dtype))

    def __add__(self, other) :
        """
        Add an :class:`MVPolyDict` to another, or to a number; 
        return an :class:`MVPolyDict`.
        """
        a = self.coef
        if isinstance(other, MVPolyDict) :
            b = other.coef
        elif isinstance(other, numbers.Number) :
            m = MVPolyDict()
            m[0] = other
            b = m.coef
        else :
            raise TypeError, "cannot add MVPolyDict to %s" % type(other)
        return MVPolyDict(mvpoly.util.dict.sum(a, b), dtype = self.dtype)


    def __radd__(self, other) :
        """
        As add, but with the types in the opposite order -- this is
        routed to add.
        """
        return self.__add__(other)


    def __mul__(self, other) :
        """
        Product of polynomials, or of a polynomial and a number.
        """
        d = {}
        if isinstance(other, MVPolyDict) :
            for k1, v1 in other.coef.iteritems() :
                m1 = MVPolyDictMonomial(key = k1)
                for k2, v2 in self.coef.iteritems() :
                    m2 = MVPolyDictMonomial(key = k2)
                    k = (m1 * m2).key
                    v = v1 * v2 + d.get(k, 0)
                    d[k] = v
            for k, v in d.items() :                
                if v == 0 :
                    d.pop(k, None)
        elif isinstance(other, numbers.Number) :
            if other != 0 :
                for k, v in self.coef.iteritems() :
                    d[k] = other * v
        else :
            raise TypeError, \
                "cannot multiply MVPolyDict by %s" % type(other)
        return MVPolyDict(d, dtype = self.dtype)


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
        d = mvpoly.util.dict.negate(self.coef)
        return MVPolyDict(d, dtype = self.dtype)


    def __eq__(self, other) :
        """
        Equality of polynomials. 
        """
        return self.coef == other.coef


    def rmf_eval(self, *args) :
        """
        Both :meth:`eval` and :meth:`compose` are routed to
        this method, which performs the evaluation of polynomials
        by a depth-first pre-order traversal of a tree derived from
        the polynomial: a simplified form of the algorithm described in 
        W. C. Rheinboldt, 
        C. K. Mesztenyi,
        J. M. Fitzgerald,
        *On the evaluation of multivariate polynomials and their
        derivatives*, 
        BIT 17 (1977), 
        437–450.
        """
        nodes = [EvalNode(k, v) for k, v in self.coef.items()]
        if self.__getitem__(0) == 0 :
            nodes += [EvalNode((), np.array(0))]
        nodes.sort(key = lambda x : x.index)

        deltas = [node1.delta(node2) 
                  for node1, node2 in zip(nodes[1:], nodes)] + [-1]

        M = self.homdeg()
        s = [ nodes[0].coef ] + [0] * M
        i = [0] * M
        m = 0
        k = 0

        nodes = nodes[1:]
        N = len(nodes)

        while m < N :
            while True :
                i[k] = nodes[m].index[k]
                if k < nodes[m].order - 1 :
                    s[k+1] = 0
                else :
                    s[k+1] = nodes[m].coef
                    m += 1
                    if k >= deltas[m] :
                        break
                k += 1
            while True :
                # cannot use += here, baffled? see
                # http://stackoverflow.com/questions/20133767
                s[k] = s[k] + s[k+1] * args[i[k]]
                s[k+1] = 0
                if (k == 0) or (k == deltas[m]) :
                    break
                else :
                    k -= 1
        return s[0]

    def order(self) :
        """
        Return the maximal order of each of the variables of
        the polynomial as a tuple of integers
        """
        n = self.maxvar
        idxs = [ MVPolyDictMonomial(key = key).index_of_length(n) for
                 key in self.coef.keys() ]
        if idxs == [] :
            ords = [] 
        elif idxs == [()] :
            ords = [0]
        else :
            ords = [max(idx[i] for idx in idxs) for i in range(n)] 
        return tuple(ords)


    def homdeg(self) :
        """
        The *homogeneous degree*, the maximal sum of the
        monomial degrees of monomials with nonzero coefficients. 
        This method will raise an error (ValueError) is called
        on the zero polynomial.
        """
        degs = [np.sum(MVPolyDictMonomial(key = k).dict.values())
                for k in self.coef.keys()]
        if not degs :
            raise ValueError("homogeneous degree undefined for zero polynomial")
        return max(degs)


    def eval(self, *args) :
        """
        Evaluate the polynomial at the points given by *args*.
        There should be as many arguments as the polynomial 
        has variables.  The argument can be numbers, or arrays
        (all of the same shape).
        """
        if len(set(np.array(arg).shape for arg in args)) != 1 :
            raise ValueError("eval() with arguments of differing shapes")
        return self.rmf_eval(*args);


    def compose(self, *args) :
        """
        Compose polynomials. The arguments, which should be
        :class:`MVPolyDict` polynomials, are substituted 
        into the corresponding variables of the polynomial.
        """
        return self.rmf_eval(*args);


    def diff(self, *args) :
        """
        Differentiate polynomial. The integer arguments
        should indicate the number to times to differentiate
        with respect to the corresponding polynomial variable,
        hence ``p.diff(0,1,1)`` would correspond to 
        :math:`\partial^2 p / \partial y \partial z`.
        """
        def diff2(idx, m0, m0_coef) :
            m0_dict  = m0.dict
            m1_dict = {}
            for i, n in enumerate(idx) :
                m0i = m0_dict.get(i, 0)
                if m0i < n :
                    return (None, 0)
                if m0i == n :
                    continue
                m1_dict[i] = m0i - n
                for k in range(n) :
                    m0_coef *= (m0i - k)
            return (MVPolyDictMonomial(dict = m1_dict), m0_coef)

        d = {}
        for m0_key, m0_coef in self.coef.iteritems() :
            m0 = MVPolyDictMonomial(key = m0_key)
            m1, m1_coef = diff2(args, m0, m0_coef)
            if m1 is not None :
                d[m1.key] = m1_coef

        return MVPolyDict(d, dtype = self.dtype)


    def int(self, *args, **kwargs) :
        """
        Indefinite integral of polynomial. The arguments are
        as for :meth:`diff`.
        """
        dtype = np.dtype(kwargs.get('dtype', self.dtype))
        if dtype.kind in set(['i', 'u']) :
            msg = "integral output of type %s" % (dtype.name)
            warnings.warn(msg, RuntimeWarning)

        def int2(idx, m0, m0_coef) :
            m1_coef = m0_coef.copy()
            m1_dict = {}
            for i, n in enumerate(idx) :
                m0i = m0.dict.get(i, 0)
                if m0i + n == 0 :
                    continue
                m1_dict[i] = m0i + n
                for k in range(n) :
                    m1_coef /= (m0i + k + 1)
            return (MVPolyDictMonomial(dict = m1_dict), m1_coef)

        d = {}
        for m0_key, m0_coef in self.coef.iteritems() :
            m0 = MVPolyDictMonomial(key = m0_key)
            m1, m1_coef = int2(args, m0, m0_coef)
            d[m1.key] = m1_coef

        return MVPolyDict(d, dtype = dtype)

class EvalNode(object) :
    """
    Helper class for the :meth:`__call__` method.
    """
    def __init__(self, key, coef) :
        self._index = MVPolyDictMonomial(key = key).occurences
        self._coef = coef.copy()

    @property
    def index(self) :
        return self._index

    @property
    def coef(self) :
        return self._coef

    @property 
    def order(self) :
        return len(self._index)

    def delta(self, other) :
        """
        The minimal index of :meth:`index` property such that the 
        `self` and `other` differ. 
        """
        n1 = len(self.index)
        n2 = len(other.index)
        for i in range(min(n1, n2)) :
            if self.index[i] != other.index[i] :
                return i
        if n1 > n2 :
            return n2
        return 0


class MVPolyDictMonomial(object) :
    """
    A class of sparse monomials, represented internally as a 
    dict of variable numbers mapped to variable orders (so that
    ``{0:2, 2:3}`` represents :math:`x^2 z^3`).  These can be
    serialised to a hashable :meth:`key` or expressed in a dense
    index (the above monomial has length-4 index of ``(2, 0, 3, 0)``).
    """
    def __init__(self, dict = None, key = None, index = None) :
        if dict is None :
            self._dict = {}
            if key is not None :
                self.key = key
            elif index is not None :
                self.index = index
        else :
            self._dict = dict

    @property
    def dict(self) :
        """
        The dictionary.
        """
        return self._dict

    @dict.setter
    def dict(self, d) :
        self._dict = d

    @property
    def key(self) :
        """
        A hashable representation (as a tuple of pairs) of the
        dictionary.
        """
        return tuple([(k, self.dict[k]) for k in sorted(self.dict.keys())])

    @key.setter
    def key(self, kvs) :
        self._dict = {k: v for (k, v) in kvs}

    @property
    def index(self) :
        """
        The monomial as an tuple of variable exponents up to the
        last variable with nonzero exponent;
        thus ``m.index`` would return ``(3, 2)``
        if ``m`` represents the monomial :math:`x^3 y^2`.
        """
        n = mvpoly.util.common.max_or_default(self.dict.keys(), -1) + 1
        return self.index_of_length(n)

    @index.setter
    def index(self, idx) :
        if hasattr(idx, "__getitem__") :
            self._dict = {k: v for (k, v) in enumerate(idx) if v != 0}
        else :
            self._dict = {} if idx == 0 else {0: idx}

    def index_of_length(self, n) :
        """
        Return the monomial as an *n*-tuple of variable exponents;
        thus ``m.index_of_length(3)`` would return ``(3, 2, 0)``
        if ``m`` represents the monomial :math:`x^3y^2`.
        """
        return tuple([self.dict.get(k, 0) for k in range(n)])

    @property
    def occurences(self) :
        """
        The monomial as a tuple of variable indices repeated
        as many times as the exponent of the variable;
        thus ``m.occurences`` would return ``(0, 0, 0, 1, 1)``
        if ``m`` represents the monomial :math:`x^3 y^2`. The 
        length of this vector is the :attr:`order` of the 
        monomial.
        """
        return tuple(i for i, e in enumerate(self.index) for _ in range(e))

    @property
    def order(self) :
        """
        The order of the monomial: the sum of exponents.
        """
        return sum(self.dict.itervalues())

    def __mul__(self, other) :
        """
        Return the product of monomials.
        """
        d = mvpoly.util.dict.merge_dicts(self.dict, other.dict, lambda x, y : x+y) 
        return MVPolyDictMonomial(dict = d)
        
