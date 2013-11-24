from mvpoly.dict import *
import numpy as np
import unittest
import warnings

class TestMVPolyDictMonomial(unittest.TestCase) :

    def test_construct_from_empty(self) :
        obt = MVPolyDictMonomial().dict
        self.assertTrue(obt == {},
                        "bad constructor:\n%s" % repr(obt))

    def test_construct_from_dict(self) :
        exp = {0:3, 5:2}
        obt = MVPolyDictMonomial(exp).dict
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))

    def test_construct_from_kw_dict(self) :
        exp = {0:3, 5:2}
        obt = MVPolyDictMonomial(dict = exp).dict
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))
    
    def test_set_dict(self) :
        exp = {0:3, 5:2}
        m = MVPolyDictMonomial()
        m.dict = exp
        obt = m.dict
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))
    
    def test_construct_from_key(self) :
        exp = ((0, 3), (5, 2))
        m = MVPolyDictMonomial(key = exp)
        obt = m.key
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))
    
    def test_set_key(self) :
        exp = ((0, 3), (5, 2))
        m = MVPolyDictMonomial()
        m.key = exp
        obt = m.key
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))

    def test_construct_from_index(self) :
        exp = (3, 0, 1, 0)
        m = MVPolyDictMonomial(index = exp)
        obt = m.index_of_length(4)
        self.assertTrue(obt == exp,
                        "bad constructor:\n%s" % repr(obt))

    def test_set_index(self) :
        exp = (3, 0, 0, 0, 0, 2)
        m = MVPolyDictMonomial()
        m.index = exp
        obt = m.index_of_length(6)
        self.assertTrue(obt == exp, "bad index:\n%s" % repr(obt))

    def test_get_index(self) :
        for idx in [ (3, 0, 0, 1), (1,), () ] :
            m = MVPolyDictMonomial()
            m.index = idx
            self.assertTrue(m.index == idx,
                            "bad index:\n%s" % repr(m.index))
        m = MVPolyDictMonomial(index = (3, 3, 0, 0))        
        self.assertTrue(m.index == (3, 3),
                        "bad index:\n%s" % repr(m.index))

    def test_index_of_zeros(self) :
        exp = ()
        for index in [(0), (0, 0), (0, 0, 0)] :
            obt = MVPolyDictMonomial(index = index).key
            self.assertTrue(obt == exp,
                            "bad index-of-zeros key:\n%s" % repr(obt))

    def test_zero_mononomial(self) :
        m = MVPolyDictMonomial(dict = {})
        obt = m.dict
        self.assertTrue(obt == {},
                        "zero poly bad dict:\n%s" % repr(obt))
        obt = m.key
        self.assertTrue(obt == (),
                        "zero poly bad key:\n%s" % repr(obt))
        obt = m.index_of_length(4)
        self.assertTrue(obt == (0, 0, 0, 0),
                        "zero poly bad idx:\n%s" % repr(obt))

    def test_nonzero_mononomial(self) :
        m = MVPolyDictMonomial(dict = {0:3, 3:1})
        obt = m.dict
        self.assertTrue(obt == {0:3, 3:1},
                        "zero poly bad dict:\n%s" % repr(obt))
        obt = m.key
        self.assertTrue(obt == ((0, 3), (3, 1)),
                        "zero poly bad key:\n%s" % repr(obt))
        obt = m.index_of_length(4)
        self.assertTrue(obt == (3, 0, 0, 1),
                        "zero poly bad idx:\n%s" % repr(obt))

    def test_multiply_mononomial(self) :
        m1 = MVPolyDictMonomial(index = (2, 0, 0, 1))
        m2 = MVPolyDictMonomial(index = (0, 2, 0, 1))
        obt = (m1 * m2).index_of_length(4)
        self.assertTrue(obt == (2, 2, 0, 2),
                        "bad product index:\n%s" % repr(obt))

    def test_occurences(self) :
        m = MVPolyDictMonomial(index = (3, 2))
        self.assertTrue(m.occurences == (0, 0, 0, 1, 1), m.occurences)

    def test_order(self) :
        for pair in [(0, ()), (3, (3,)), (8, (7, 1, 0))] :
            exp, index = pair
            m = MVPolyDictMonomial(index = index)
            obt = m.order
            self.assertTrue(obt == exp, obt)


class TestMVPolyDict(unittest.TestCase) :

    def test_construct_from_empty(self) :
        exp = {}
        obt = MVPolyDict().coef
        self.assertTrue(isinstance(obt, dict))
        self.assertTrue(exp == obt,
                        "bad constructor:\n%s" % repr(obt))

    def test_construct_from_dict(self) :
        exp = {((2,3),): 9,
               ((1,2),): 8}
        obt = MVPolyDict(exp, dtype = int).coef
        self.assertTrue(exp == obt,
                        "bad constructor:\n%s" % repr(obt))

    def test_construct_from_monomials(self) :
        x, y = MVPolyDict.monomials(2)
        p = x + 2*y + 3
        exp = {((0, 1),) : 1,
               ((1, 1),) : 2,
               ()        : 3}
        obt = p.coef
        self.assertTrue(exp == obt,
                        "bad constructor:\n%s %s" % (repr(obt), repr(exp)))

    def test_construct_from_monomials_zero_coefs(self) :
        x, y = MVPolyDict.monomials(2)
        p = 0*x + 0*y + 0
        exp = {}
        obt = p.coef
        self.assertTrue(exp == obt,
                        "bad constructor:\n%s %s" % (repr(obt), repr(exp)))


class TestMVPolyDictDtype(unittest.TestCase) :

    def setUp(self) :
        d =  {((2,3),): 9,
              ((1,2),): 8}
        self.f = MVPolyDict(d.copy(), dtype = np.float32) 
        self.i = MVPolyDict(d.copy(), dtype = np.int16) 

    def test_construct_dtype_of_coef_explict(self) :
        t = self.f[0, 2].dtype
        self.assertTrue(t == np.float32, "bad dtype: %s" % repr(t))
        t = self.i[0, 2].dtype
        self.assertTrue(t == np.int16, "bad dtype: %s" % repr(t))

    def test_construct_dtype_of_coef_implict(self) :
        t = self.f[0, 0].dtype
        self.assertTrue(t == np.float32, "bad dtype: %s" % repr(t))
        t = self.i[0, 0].dtype
        self.assertTrue(t == np.int16, "bad dtype: %s" % repr(t))

    def test_construct_get_dtype(self) :
        self.assertTrue(self.f.dtype == np.float32,
                        "bad dtype: %s" % repr(self.f.dtype))
        self.assertTrue(self.i.dtype == np.int16,
                        "bad dtype: %s" % repr(self.i.dtype))

    def test_construct_set_dtype(self) :
        self.f.dtype = bool
        self.assertTrue(self.f.dtype == bool,
                        "bad dtype: %s" % repr(self.f.dtype))

    def test_construct_dtype_persist(self) :
        p = self.i
        qs = [p+p, p+1, 1+p, p*p, 2*p, p*2, p**3, 2*p]
        for q in qs :
            self.assertTrue(q.dtype == np.int16,
                            "bad dtype: %s" % repr(q.dtype))

    def test_assign_dtype(self) :
        self.f[0, 7] = 4
        t = self.f[0, 7].dtype
        self.assertTrue(t == np.float32, "bad dtype: %s" % repr(t))

class TestMVPolyDictNumvar(unittest.TestCase) :

    def test_numvar_from_dict_constructor(self) :
        d =  {((2,3),): 6,
              ((1,2),): 8}
        p = MVPolyDict(d, dtype = np.int32)
        self.assertTrue(p.numvar == 2, 
                        "bad number of variables:\n%s" % p.numvar)
        self.assertTrue(p.maxvar == 3, 
                        "bad maximal variable:\n%s" % p.maxvar)

    def test_numvar_from_set(self) :
        p = MVPolyDict(dtype = np.int32)
        p[0, 0, 3] = 17
        self.assertTrue(p.numvar == 1, 
                        "bad number of variables:\n%s" % p.numvar)
        self.assertTrue(p.maxvar == 3, 
                        "bad number of variables:\n%s" % p.maxvar)


class TestMVPolyDictOrder(unittest.TestCase) :

    def test_order_zero(self) :
        p = MVPolyDict(dtype = np.int32)
        exp = ()
        obt = p.order()
        self.assertTrue(exp == obt,
                        "bad order:\n%s" % repr(obt))

    def test_order_constant(self) :
        p = MVPolyDict({():2}, dtype = np.int32)
        exp = (0,)
        obt = p.order()
        self.assertTrue(exp == obt,
                        "bad order:\n%s" % repr(obt))

    def test_order_1d(self) :
        p = MVPolyDict({():1, ((0,1),):2, ((0,2),):1}, dtype = np.int32)
        exp = (2,)
        obt = p.order()
        self.assertTrue(exp == obt,
                        "bad order:\n%s" % repr(obt))

    def test_order_2d(self) :
        p = MVPolyDict({():1, ((0,1),):1, ((2,2),):1}, dtype = np.float64)
        exp = (1, 0, 2)
        obt = p.order()
        self.assertTrue(exp == obt,
                        "bad order:\n%s" % repr(obt))


class TestMVPolyDictSetget(unittest.TestCase) :

    def test_set_constant(self) :
        p = MVPolyDict()
        p[0] = 3
        self.assertTrue(p[0] == 3, "bad set:\n%s" % repr(p[0]))
        self.assertTrue(p[0, 0] == 3, "bad set:\n%s" % repr(p[0, 0]))
        self.assertTrue(p.order() == (0,), repr(p.order()))

    def test_setget(self) :
        exp = 3
        p = MVPolyDict()
        p[3, 2, 1] = exp
        obt = p[3, 2, 1]
        self.assertTrue(exp == obt,
                        "bad set/get:\n%s" % repr(obt))

    def test_get_unset(self) :
        p = MVPolyDict()
        exp = 0
        obt = p[1, 2, 3]
        self.assertTrue(exp == obt,
                        "bad get unset:\n%s" % repr(obt))


class TestMVPolyDictAddSub(unittest.TestCase) :

    def setUp(self) :
        self.A = MVPolyDict(dtype = int)
        self.A[0, 0] = 1
        self.A[1, 0] = 2
        self.A[2, 0] = 3
        self.B = MVPolyDict(dtype = int)
        self.B[0, 0] = 1
        self.B[0, 1] = 1

class TestMVPolyDictAdd(TestMVPolyDictAddSub) :

    def test_add1(self) :
        C = self.A + self.B
        obt = [ [ C[i,j] for i in range(3) ] for j in range(2) ]
        exp = [[2, 2, 3], [1, 0, 0]]
        self.assertTrue(exp == obt,
                        "bad sum:\n%s" % repr(obt))

    def test_add2(self) :
        C = self.A + 1
        exp = [2, 2, 3]
        obt = [C[i] for i in range(3)]
        self.assertTrue(exp == obt,
                        "bad sum:\n%s" % repr(obt))

    def test_add3(self) :
        C = 1 + self.A
        exp = [2, 2, 3]
        obt = [C[i] for i in range(3)]
        self.assertTrue(exp == obt,
                        "bad sum:\n%s" % repr(obt))

    def test_add4(self) :
        C = MVPolyDict()
        for i, Ci in enumerate([2, 1, 0, 3]) :
            C[i] = Ci
        D = C + self.A
        obt = [D[i] for i in range(4)]
        exp = [3, 3, 3, 3]
        self.assertTrue(exp == obt,
                        "bad sum:\n%s" % repr(obt))


class TestMVPolyDictSubtract(TestMVPolyDictAddSub) :
    
    def test_subtract(self) :
        C = self.A - self.B
        obt = [ [ C[i,j] for i in range(3) ] for j in range(2) ]
        exp = [[0, 2, 3], [-1, 0, 0]]
        self.assertTrue(exp == obt,
                        "bad sum:\n%s" % repr(obt))


class TestMVPolyDictMultiply(unittest.TestCase) :

    def setUp(self) :
        A = MVPolyDict()
        A[0] = A[1] = 1
        self.A = A
        B = MVPolyDict()
        for i in range(2) :
            for j in range(3) :
                B[i, j] = 1
        self.B = B

    def test_multiply_scalar(self) :
        exp = [2, 2] 
        for C in [2 * self.A, self.A * 2] :
            obt = [C[n] for n in range(2)]
            self.assertTrue(exp == obt,
                            "bad multiply:\n%s" % repr(obt))

    def test_multiply_1d(self) :
        C = self.A * self.A
        obt = [C[n] for n in range(3)]
        exp = [1, 2, 1]
        self.assertTrue(exp == obt,
                        "bad multiply:\n%s" % repr(obt))

    def test_multiply_dimension(self) :
        exp = [[1, 1], [2, 2], [1, 1]] 
        for C in [self.A * self.B, self.B * self.A] :
            obt = [[C[i,j] for j in range(2)] for i in range(3)] 
            self.assertTrue(exp == obt,
                            "bad multiply:\n%s" % repr(obt))

    def test_multiply_arithmetic(self) :
        x, y = MVPolyDict.monomials(2, dtype = int)
        p = (x + y)*(2*x - y)
        q = 2*x**2 + x*y - y**2
        self.assertTrue(p == q,
                        "bad multiply:\n%s\n%s" % (repr(p.coef), 
                                                   repr(q.coef)))

    def test_multiply_complex(self) :
        x, y = MVPolyDict.monomials(2, dtype = complex)
        p = (x + y)*(x + 1j*y)
        q = x**2 + (1 + 1j)*x*y + 1j*y**2
        self.assertTrue(p == q,
                        "bad multiply:\n%s\n%s" % (repr(p.coef), 
                                                   repr(q.coef)))


class TestMVPolyDictEval(unittest.TestCase) :

    def makep(self, x, y) :
        return x**2 + 2*x*y + 3*y + 4*y**2 + 5

    def setUp(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        self.p = self.makep(x, y)
        self.x = [1, 1, -1, 0,  7, 3,  -3, 1]
        self.y = [1, 0,  0, 3, -1, 2, -10, 2]
        self.n = len(self.x)

    def test_eval_point(self) :
        for i in range(self.n) :
            obtained = self.p.eval(self.x[i], self.y[i])
            expected = self.makep(self.x[i], self.y[i])
            self.assertTrue(expected == obtained,
                            "bad eval: %s != %s" % ( repr(obtained), 
                                                     repr(expected) ))

    def test_eval_array_1d(self) :
        obtained = self.p.eval(self.x, self.y)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_array_2d(self) :
        n = self.n
        x = np.reshape(self.x, (2, n/2))
        y = np.reshape(self.y, (2, n/2))
        obtained = self.p.eval(x, y)
        self.assertTrue(obtained.shape == (2, n/2))
        obtained.shape = (n,)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_badargs(self) :
        self.assertRaises(ValueError, self.p.eval, self.x[1:], self.y)

    def test_eval_dtype(self) :
        for dt in [int, float] :
            x, y = MVPolyDict.monomials(2, dtype=dt)
            p = self.makep(x, y)
            self.assertTrue(p.dtype == dt)
            xg = np.array([1, 2], dtype=dt)
            yg = np.array([-2, 0], dtype=dt)
            self.assertTrue(p.eval(xg, yg).dtype == dt, "bad type")

    def test_eval_univar(self) :
        x, = MVPolyDict.monomials(1)
        p = x**2 + 1
        self.assertTrue(p.eval(2) == 5, "univar")

    def test_eval_1d_in_2d(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = x**2 + 1
        self.assertTrue(p.eval(2, 1) == 5, "2 in 1")

    def test_eval_return_type(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = x**2 + y
        self.assertTrue(isinstance(p.eval(2, 1), int), "int return")

    def test_eval_complex(self) :
        x, y = MVPolyDict.monomials(2, dtype=np.complex)
        p = x**2 - y
        self.assertTrue(p.eval(1.0j, 1.0) == -2, "complex eval") 


class TestMVPolyDictDiff(unittest.TestCase) :

    def test_diff_1d(self) :
        x, = MVPolyDict.monomials(1)
        p = x**5 + 2*x**2 + 1
        exp = 5*x**4 + 4*x
        obt = p.diff(1)
        self.assertTrue(exp == obt,
                        "bad 1D-derivative\n%s\n%s" % \
                            (repr(obt), repr(exp)))

    def test_diff_2d(self) :
        x, y = MVPolyDict.monomials(2, dtype = int)
        p = x**2 + x*y + y**3
        exp = 2*x + y 
        obt = p.diff(1, 0)
        self.assertTrue(exp == obt,
                        "bad x-derivative\n%s\n%s" % \
                            (repr(obt.coef), repr(exp.coef)))
        exp = x + 3*y**2
        obt = p.diff(0, 1)
        self.assertTrue(exp == obt,
                        "bad y-derivative\n%s\n%s" % \
                            (repr(obt), repr(exp)))

    def test_diff_dtype(self) :
        for dt in (np.int32, np.float64) :
            x, y = MVPolyDict.monomials(2, dtype=dt)
            p = 2*x**2 + 3*y**3
            exp = dt
            obt = p.diff(2,1).dtype
            self.assertTrue(exp == obt, 
                            "bad datatype %s %s" % \
                                (repr(obt), repr(exp)))

    def test_diff_invariant(self) :
        x, y = MVPolyDict.monomials(2, dtype = int)
        p  = x + 2*y
        exp = p.coef.copy()
        q = p.diff(1,0)
        obt = p.coef
        self.assertTrue(exp == obt, 
                        "polynomial modified by diff %s" % \
                            (repr(obt)))


class TestMVPolyDictInt(unittest.TestCase) :

    def test_int_1d(self) :
        x, = MVPolyDict.monomials(1, dtype = np.double)
        p = 5*x**4 + 4*x
        expected = x**5 + 2*x**2
        obtained = p.int(1)
        self.assertTrue(expected == obtained,
                        "bad 1D indefinite integral \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int2_1d(self) :
        x, = MVPolyDict.monomials(1, dtype = np.double)
        p = 6*x + 2
        expected = (x + 1) * x**2
        obtained = p.int(2)
        self.assertTrue(expected == obtained,
                        "bad 1D indefinite integral \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_2d_x(self) :
        x, y = MVPolyDict.monomials(2, dtype = np.double)
        p = 3*x**2 + 4*x*y + 3*y**2
        expected = x**3 + 2*y*(x**2) + 3*x*y**2
        obtained = p.int(1, 0)
        self.assertTrue(expected == obtained,
                        "bad indefinite integral (x) \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_2d_y(self) :
        x, y = MVPolyDict.monomials(2, dtype = np.double)
        p = 3*x**2 + 4*x*y + 3*y**2
        expected = 3*y*x**2 + 2*x*y**2 + y**3
        obtained = p.int(0, 1)
        self.assertTrue(expected == obtained,
                        "bad indefinite integral (y) \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_invariant(self) :
        x, = MVPolyDict.monomials(1, dtype = np.double)
        p0 = 2*x
        p1 = 2*x
        p0.int(1)
        self.assertTrue(p0 == p1, 
                        "ingtegration side-effect %s %s" % \
                            (repr(p0.coef), repr(p1.coef)))
        
    def test_int_dtype(self) :
        for dt in [np.float32, np.float64, np.complex] :
            x, y = MVPolyDict.monomials(2, dtype = int)
            p = (x+y)**2
            q = p.int(1, 1, dtype=dt)
            expected = dt
            obtained = q.dtype
            self.assertTrue(expected == obtained, 
                            "bad datatype %s %s" % \
                                (repr(obtained), repr(expected)))

    def test_int_integer_warning(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = 3*x + 4*y
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            p.int(1, 1)
            self.assertTrue(len(w), "expected 1 warning, got %i" % (len(w)))
            wcat = w[0].category
            self.assertTrue(issubclass(wcat, RuntimeWarning),
                            "expected RuntimeWarning, got %s" % (wcat))


class TestMVPolyDictCompose(unittest.TestCase) :
    
    def test_compose_1d(self) :
        x, = MVPolyDict.monomials(1, dtype=int)
        p = x**2 + 1
        q = p.compose(x-1)
        expected = (x-1)**2 + 1
        obtained = q
        self.assertTrue(expected == obtained, 
                        "bad compose\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_compose_2d(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = x**2 + y + 1
        q = p.compose(2*y, x)
        expected = (2*y)**2 + x + 1
        obtained = q
        self.assertTrue(expected == obtained, 
                        "bad compose\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_compose_distribute_over_eval(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = (x + 3*y - 1)**2
        u = x - y
        v = x + y
        for i in range(5) :
            for j in range(5) :
                expected = p.compose(u, v).eval(i, j)
                obtained = p.eval(u.eval(i, j), v.eval(i, j))
                self.assertTrue(expected == obtained, 
                                "bad compose\n%s\n%s" % \
                                    (repr(obtained), repr(expected)))

    def test_call_compose(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = x + y
        self.assertTrue(isinstance(p(1, y), MVPolyDict), "bad call/compose")
        self.assertTrue(isinstance(p(1, 2), int), "bad call/eval")

    def test_compose_1of2(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)        
        p = x + 1
        q = p.compose(y, x)
        self.assertTrue(q(1, 0) == 1, "bad compose")


class TestMVPolyDictHomdeg(unittest.TestCase) :

    def test_homdeg_zero(self) :
        p = MVPolyDict.zero(dtype=int)
        self.assertRaises(ValueError, p.homdeg)

    def test_homdeg_1d(self) :
        x, = MVPolyDict.monomials(1, dtype=int)
        p = x**5 + x + 3
        obtained = p.homdeg()
        expected = 5
        self.assertTrue(expected == obtained, 
                        "bad homdeg %s" % \
                            repr(obtained))

    def test_homdeg_2d(self) :
        x, y = MVPolyDict.monomials(2, dtype=int)
        p = (x**5 + x + 3)*y**2 + y 
        obtained = p.homdeg()
        expected = 7
        self.assertTrue(expected == obtained, 
                        "bad homdeg %s" % \
                            repr(obtained))


class TestMVPolyDictMisc(unittest.TestCase) :

    def test_euler_goldbach(self) :
        """
        Euler's four-square identity, discussed in 1749 in a letter 
        from Euler to Goldbach. 
        """
        a1, a2, a3, a4, b1, b2, b3, b4 = MVPolyDict.monomials(8, dtype = int) 
        p = (a1**2 + a2**2 + a3**2 + a4**2) * (b1**2 + b2**2 + b3**2 + b4**2)
        q = (a1*b1 - a2*b2 - a3*b3 - a4*b4)**2 + \
            (a1*b2 + a2*b1 + a3*b4 - a4*b3)**2 + \
            (a1*b3 - a2*b4 + a3*b1 + a4*b2)**2 + \
            (a1*b4 + a2*b3 - a3*b2 + a4*b1)**2
        self.assertTrue(p == q,
                        "bad multiply:\n%s\n%s" % (repr(p.coef), 
                                                   repr(q.coef)))
        
