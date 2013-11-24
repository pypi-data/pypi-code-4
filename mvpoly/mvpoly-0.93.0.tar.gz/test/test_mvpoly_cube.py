from mvpoly.cube import *
import numpy as np
import warnings
import unittest

class TestMVPolyCube(unittest.TestCase) :

    def test_construct_from_empty(self) :
        obtained = MVPolyCube().coef
        expected = []
        self.assertTrue((expected == obtained).all(),
                        "bad constructor:\n%s" % repr(obtained))


class TestMVPolyCubeDtype(unittest.TestCase) :

    def setUp(self) :
        a = [1, 2, 3, 4]
        self.f = MVPolyCube(a, dtype=float) 
        self.i = MVPolyCube(a, dtype=int) 

    def test_construct_get_dtype(self) :
        self.assertTrue(self.f.dtype == float,
                        "bad dtype: %s" % repr(self.f.dtype))
        self.assertTrue(self.i.dtype == int,
                        "bad dtype: %s" % repr(self.i.dtype))

    def test_construct_set_dtype(self) :
        self.f.dtype = bool
        self.assertTrue(self.f.dtype == bool,
                        "bad dtype: %s" % repr(self.f.dtype))

    def test_construct_dtype_persist(self) :
        p = MVPolyCube([1, 2], dtype = int) 
        qs = [p+p, p+1, 1+p, p*p, 2*p, p*2, p**3, 2*p]
        for q in qs :
            self.assertTrue(q.dtype == int,
                            "bad dtype: %s" % repr(q.dtype))

    def test_construct_dtype_delegated(self) :

        def check_dtype(self, p, dtype) :
            self.assertTrue(p.dtype == dtype,
                            "bad dtype: %s" % repr(p.dtype))
            self.assertTrue(p.coef.dtype == dtype,
                            "bad base dtype: %s" % repr(p.coef.dtype))

        p = MVPolyCube([1, 2], dtype = int) 
        check_dtype(self, p, int)
        p.dtype = float
        check_dtype(self, p, float)
        p.dtype = complex
        check_dtype(self, p, complex)

class TestMVPolyCubeOrder(unittest.TestCase) :

    def test_order_zero(self) :
        p = MVPolyCube.zero()
        expected = ()
        obtained = p.order()
        self.assertTrue(expected == obtained,
                        "bad order:\n%s" % repr(obtained))

    def test_order_1d(self) :
        p = MVPolyCube([1, 2, 3])
        expected = (2,)
        obtained = p.order()
        self.assertTrue(expected == obtained,
                        "bad order:\n%s" % repr(obtained))

    def test_order_2d(self) :
        p = MVPolyCube([[1, 2, 3], [4, 5, 6]])
        expected = (1, 2)
        obtained = p.order()
        self.assertTrue(expected == obtained,
                        "bad order:\n%s" % repr(obtained))


class TestMVPolyCubeEqual(unittest.TestCase) :

    def test_equal_self(self) :
        p = MVPolyCube([[1, 2, 3], [4, 5, 6]])
        self.assertTrue(p == p, "bad equality")

    def test_equal_diffsize(self) :
        p = MVPolyCube([[1, 2, 0], [4, 5, 0]])
        q = MVPolyCube([[1, 2], [4, 5]])
        self.assertTrue(p == q, "bad equality")

    def test_equal_diffdim(self) :
        p = MVPolyCube([[1, 2, 3], [0, 0, 0]])
        q = MVPolyCube([1, 2, 3])
        self.assertTrue(p == q, "bad equality")

    def test_unequal(self) :
        p = MVPolyCube([1, 2, 3])
        q = MVPolyCube([1, 2, 3, 4])
        self.assertFalse(p == q, "bad equality")
        self.assertTrue(p != q, "bad non-equality")


class TestMVPolyCubeAdd(unittest.TestCase) :

    def setUp(self) :
        self.A = MVPolyCube([1, 2, 3])
        self.B = MVPolyCube([[1], [1]])

    def test_add1(self) :
        obtained = (self.A + self.B).coef
        expected = [[2, 2, 3], [1, 0, 0]]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add2(self) :
        obtained = (self.A + 1).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add3(self) :
        obtained = (1 + self.A).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add4(self) :
        obtained = ([2, 1, 0, 3] + self.A).coef
        expected = [3, 3, 3, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n%s" % repr(obtained))

    def test_add_dtype(self) :
        A = self.A
        A.dtype = int
        B = A + A
        self.assertTrue(B.dtype == int,
                        "bad sum dtype:\n%s" % repr(B.dtype))


class TestMVPolyCubeMultiply(unittest.TestCase) :
    
    def setUp(self) :
        self.A = MVPolyCube([1, 1], dtype = int)
        self.B = MVPolyCube([[1, 1], [1, 1]], dtype = int)

    def test_multiply_scalar(self) :
        obtained = (2 * self.A).coef
        expected = [2, 2]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n%s" % repr(obtained))

    def test_multiply_1d(self) :
        obtained = (self.A * self.A).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n%s" % repr(obtained))

    def test_multiply_dtype(self) :
        self.A.dtype = int
        C = self.A * self.A
        self.assertTrue((C.dtype == int),
                        "bad product type:\n%s" % repr(C.dtype))
        
    def test_multiply_dimension(self) :
        expected = [[1, 1], [2, 2], [1, 1]] 
        obtained = (self.A * self.B).coef
        self.assertTrue((expected == obtained).all(),
                        "bad AB multiply:\n%s" % repr(obtained))
        obtained = (self.B * self.A).coef
        self.assertTrue((expected == obtained).all(),
                        "bad BA multiply:\n%s" % repr(obtained))

    def test_multiply_arithmetic(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p1 = (x + y)*(2*x - y)
        p2 = 2*x**2 + x*y - y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n%s\n%s" % (repr(p1.coef), 
                                                   repr(p2.coef)))

    def test_multiply_complex(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p1 = (x + y)*(x + 1j*y)
        p2 = x**2 + (1 + 1j)*x*y + 1j*y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n%s\n%s" % (repr(p1.coef), 
                                                   repr(p2.coef)))


class TestMVPolyCubePower(unittest.TestCase) :

    def test_power_small(self) :
        A = MVPolyCube([1, 1])
        obtained = (A**2).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))
        obtained = (A**3).coef
        expected = [1, 3, 3, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))

    def test_power_types(self) :
        A = MVPolyCube([1, 1], dtype=int)
        obtained = (A**5).coef
        expected = [1, 5, 10, 10, 5, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n%s" % repr(obtained))
        self.assertTrue(obtained.dtype == int,
                        "wrong data type for power: %s" % repr(obtained.dtype))

    def test_power_badargs(self) :
        A = MVPolyCube([1, 1])
        self.assertRaises(TypeError, A.__pow__, 1.5)
        self.assertRaises(ArithmeticError, A.__pow__, -2)


class TestMVPolyCubeMonomials(unittest.TestCase) :

    def test_monomials_count(self) :
        for n in [2,3,4] :
            M = MVPolyCube.monomials(n)
            self.assertTrue(len(M) == n)

    def test_monomials_create(self) :
        x, y, z = MVPolyCube.monomials(3)
        self.assertTrue((x.coef == [[[0]],[[1]]]).all(), 
                        "bad x monomial: \n%s" % repr(x.coef))
        self.assertTrue((y.coef == [[[0],[1]]]).all(), 
                        "bad y monomial: \n%s" % repr(y.coef))
        self.assertTrue((z.coef == [[[0, 1]]]).all(), 
                        "bad z monomial: \n%s" % repr(z.coef))

    def test_monomials_build(self) :
        x, y = MVPolyCube.monomials(2)
        p = 2*x**2 + 3*x*y + 1
        self.assertTrue((p.coef == [[1, 0], [0, 3], [2, 0]]).all(),
                        "bad build: \n%s" % repr(p.coef))

    def test_monomials_dtype(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = 2*x**2 + 3*x*y + 1
        for m in (x, y, p) :
            self.assertTrue(m.dtype == int,
                            "bad type: \n%s" % repr(m.dtype))
            self.assertTrue(m.coef.dtype == int,
                            "bad type: \n%s" % repr(m.coef.dtype))


class TestMVPolyCubeGetSet(unittest.TestCase) :

    def setUp(self) :
        x, y = MVPolyCube.monomials(2)
        self.p = 2*x**2 + 3*x*y + 1

    def test_getitem(self) :
        obtained = self.p[0:2,:]
        expected = [[1, 0], [0, 3]]
        self.assertTrue((obtained == expected).all(),
                        "bad getitem:\n%s" % repr(obtained))

    def test_setitem(self) :
        self.p[0, :] = [2, 2]
        obtained = self.p.coef
        expected = [[2, 2], [0, 3], [2, 0]]
        self.assertTrue((obtained == expected).all(),
                        "bad getitem:\n%s" % repr(obtained))


class TestMVPolyCubeNeg(unittest.TestCase) :

    def test_negation(self) :
        x, y = MVPolyCube.monomials(2)
        p = 2*x**2 - 3*x*y + 1
        obtained = (-p).coef
        expected = [[-1, 0], [0, 3], [-2, 0]]
        self.assertTrue((obtained == expected).all(),
                        "bad negation:\n%s" % repr(obtained))


class TestMVPolyCubeSubtract(unittest.TestCase) :

    def test_subtract(self) :
        x, y = MVPolyCube.monomials(2)
        p = 1 - x
        q = -(x - 1)
        self.assertTrue((p.coef == q.coef).all(),
                        "bad subtract:\n%s\n%s" \
                            % (repr(p.coef), repr(q.coef)))


class TestMVPolyCubeEval(unittest.TestCase) :

    def makep(self, x, y) :
        return (1 - x**2) * (1 + y) - 8

    def setUp(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        self.p = self.makep(x, y)
        self.x = [0, 1, -1, 0,  7, 3,  -3, 1]
        self.y = [0, 0,  0, 3, -1, 2, -10, 2]
        self.n = len(self.x)

    def test_eval_point(self) :
        for i in range(self.n) :
            obtained = self.p(self.x[i], self.y[i])
            expected = self.makep(self.x[i], self.y[i])
            self.assertTrue(expected == obtained,
                            "bad eval: %s" % (repr(obtained)))

    def test_eval_array_1d(self) :
        obtained = self.p(self.x, self.y)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_array_2d(self) :
        n = self.n
        x = np.reshape(self.x, (2, n/2))
        y = np.reshape(self.y, (2, n/2))
        obtained = self.p(x, y)
        self.assertTrue(obtained.shape == (2, n/2))
        obtained.shape = (n,)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: %s" % (repr(obtained)))

    def test_eval_badargs(self) :
        self.assertRaises(AssertionError, self.p, self.x[1:], self.y)

    def test_eval_dtype(self) :
        for dt in [int, float] :
            x, y = MVPolyCube.monomials(2, dtype=dt)
            p = self.makep(x, y)
            self.assertTrue(p.dtype == dt)
            xg = np.array([1, 2], dtype=dt)
            yg = np.array([-2, 0], dtype=dt)
            self.assertTrue(p(xg, yg).dtype == dt, "bad type")

    def test_eval_regression(self) :
        for dt in [int, float] :
            x, y = MVPolyCube.monomials(2, dtype=dt)
            p = 2*x**2 + 3*y
            self.assertTrue(p(1,1) == 5, "regression A")
            p = 2*x + 3*y**2
            self.assertTrue(p(1,1) == 5, "regression B")
            x, y, z = MVPolyCube.monomials(3, dtype=dt)
            p = 3*x**2 + y + z
            self.assertTrue(p(1,1,1) == 5, "regression C")

    def test_eval_univar(self) :
        x, = MVPolyCube.monomials(1)
        p = x**2 + 1
        self.assertTrue(p(2) == 5, "univar")

    def test_eval_1d_in_2d(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = x**2 + 1
        self.assertTrue(p.eval(2, 1) == 5, "2 in 1")

    def test_eval_return_type(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = x**2 + y
        self.assertTrue(isinstance(p.eval(2, 1), int), "int return")

    def test_eval_complex(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 - y
        self.assertTrue(p.eval(1.0j, 1.0) == -2, "complex eval") 

class TestMVPolyCubeDiff(unittest.TestCase) :

    def test_diff_1d(self) :
        x, = MVPolyCube.monomials(1, dtype=float)
        p = x**5 + 2*x**2 + 1
        expected = (5*x**4 + 4*x).coef
        obtained = p.diff(1).coef
        self.assertTrue((expected == obtained).all(),
                        "bad 1D-derivative\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_diff_2d(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = x**2 + x*y + y**3
        expected = (2*x + y).coef 
        obtained = p.diff(1, 0).coef
        self.assertTrue((expected == obtained[:,0:2]).all(),
                        "bad x-derivative\n%s\n%s" % \
                            (repr(obtained),repr(expected)))
        expected = (x + 3*y**2).coef
        obtained = p.diff(0, 1).coef
        self.assertTrue((expected == obtained[0:2,:]).all(),
                        "bad y-derivative\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_diff_dtype(self) :
        for dt in (int, float) :
            x, y = MVPolyCube.monomials(2, dtype=dt)
            p = 2*x**2 + 3*y**3
            expected = dt
            obtained = p.diff(2,1).dtype
            self.assertTrue(expected == obtained, 
                            "bad datatype %s %s" % \
                                (repr(obtained), repr(expected)))

    def test_diff_invariant(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p  = x + 2*y
        expected = p.coef.copy()
        q = p.diff(1,0)
        obtained = p.coef
        self.assertTrue((expected == obtained).all(), 
                        "polynomial modified by diff %s" % \
                            (repr(obtained)))


class TestMVPolyCubeInt(unittest.TestCase) :

    def test_int_1d(self) :
        x, = MVPolyCube.monomials(1, dtype = np.double)
        p = 5*x**4 + 4*x
        expected = x**5 + 2*x**2
        obtained = p.int(1)
        self.assertTrue(expected == obtained,
                        "bad 1D indefinite integral \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_2d_x(self) :
        x, y = MVPolyCube.monomials(2, dtype = np.double)
        p = 3*x**2 + 4*x*y + 3*y**2
        expected = x**3 + 2*y*(x**2) + 3*x*y**2
        obtained = p.int(1, 0)
        self.assertTrue(expected == obtained,
                        "bad indefinite integral (x) \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_2d_y(self) :
        x, y = MVPolyCube.monomials(2, dtype = np.double)
        p = 3*x**2 + 4*x*y + 3*y**2
        expected = 3*y*x**2 + 2*x*y**2 + y**3
        obtained = p.int(0, 1)
        self.assertTrue(expected == obtained,
                        "bad indefinite integral (y) \n%s\n%s" % \
                            (repr(obtained.coef), repr(expected.coef)))

    def test_int_dtype(self) :
        for dt in [np.float32, np.float64, np.complex] :
            x, y = MVPolyCube.monomials(2, dtype=int)
            p = (x+y)**2
            q = p.int(1, 1, dtype=dt)
            expected = dt
            obtained = q.dtype
            self.assertTrue(expected == obtained, 
                            "bad datatype %s %s" % \
                                (repr(obtained), repr(expected)))

    def test_int_integer_warning(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = 3*x + 4*y
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            p.int(1, 1)
            self.assertTrue(len(w), "expected 1 warning, got %i" % (len(w)))
            wcat = w[0].category
            self.assertTrue(issubclass(wcat, RuntimeWarning),
                            "expected RuntimeWarning, got %s" % (wcat))

class TestMVPolyCubeIntDiff(unittest.TestCase) :

    def test_intdif_random(self) :
        for dt in [float, complex] :
            shp = (9, 10, 11)
            c = np.random.randint(low=-10, high=10, size=shp)
            p = MVPolyCube(c, dtype=dt)
            expected = p.coef
            obtained = p.int(1, 1, 2).diff(1, 1, 2).coef
            self.assertTrue((np.abs(expected - obtained) < 1e-10).all(),
                            "bad integrate-differentiate \n%s\n%s" % \
                                (repr(obtained), repr(expected)))


class TestMVPolyCubeCompose(unittest.TestCase) :
    
    def test_compose_1d(self) :
        x, = MVPolyCube.monomials(1, dtype=int)
        p = x**2 + 1
        q = p.compose(x-1)
        expected = ((x-1)**2 + 1).coef
        obtained = q.coef
        self.assertTrue((expected == obtained).all(), 
                        "bad compose\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_compose_2d(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = x**2 + y + 1
        q = p.compose(2*y, x)
        expected = ((2*y)**2 + x + 1).coef
        obtained = q.coef
        self.assertTrue((expected == obtained).all(), 
                        "bad compose\n%s\n%s" % \
                            (repr(obtained), repr(expected)))

    def test_compose_distribute_over_eval(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
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
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = x + y
        self.assertTrue(isinstance(p(1, y), MVPolyCube), "bad call/compose")
        self.assertTrue(isinstance(p(1, 2), int), "bad call/eval")

    def test_compose_1of2(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)        
        p = x + 1
        q = p.compose(y, x)
        self.assertTrue(q(1, 0) == 1, "bad compose")


class TestMVPolyCubeHomdeg(unittest.TestCase) :

    def test_homdeg_zero(self) :
        p = MVPolyCube.zero(dtype=int)
        self.assertRaises(ValueError, p.homdeg) 

    def test_homdeg_1d(self) :
        x, = MVPolyCube.monomials(1, dtype=int)
        p = x**5 + x + 3
        obtained = p.homdeg()
        expected = 5
        self.assertTrue(expected == obtained, 
                        "bad homdeg %s" % \
                            repr(obtained))

    def test_homdeg_2d(self) :
        x, y = MVPolyCube.monomials(2, dtype=int)
        p = (x**5 + x + 3)*y**2 + y 
        obtained = p.homdeg()
        expected = 7
        self.assertTrue(expected == obtained, 
                        "bad homdeg %s" % \
                            repr(obtained))

# this will not be added for a while, it is here just to
# check that mvpoly integration works for the author

def have_maxmodnb() :
    try:
        import maxmodnb
    except ImportError:
        return False
    return True

@unittest.skipUnless(have_maxmodnb(), "maxmodnb not installed")
class TestMVPolyCubeMaxmodnb(unittest.TestCase) :

    def test_maxmodnb_simple(self) :
        eps = 1e-10
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        expected = 2.0
        obtained = p.maxmodnb(eps = eps)[0]
        self.assertTrue(abs(expected - obtained) < eps*expected, 
                        "bad maxmodnb %s" % repr(obtained))

    def test_maxmodnb_fifomax(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(RuntimeError, p.maxmodnb, fifomax = 3)

    def test_maxmodnb_unknown_keyword(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(ValueError, p.maxmodnb, nosuchvar = 3)

    def test_maxmodnb_no_positional_args(self) :
        x, y = MVPolyCube.monomials(2, dtype=complex)
        p = x**2 + 1
        self.assertRaises(TypeError, p.maxmodnb, 3)


if __name__ == '__main__':
    unittest.main()
