import mvpoly
import mvpoly.cube
import mvpoly.dict
import numpy as np
import unittest

# each base-class method needs to be tested for each of
# the subclasses, as listed here

classes = [mvpoly.cube.MVPolyCube, 
           mvpoly.dict.MVPolyDict]

class TestMVPolyMaxmodND(unittest.TestCase) :

    def test_maxmodnd_univariate(self) :
        eps = 1e-9 
        for C in classes :
            x, = C.monomials(1, dtype=complex)
            p = x**10 + 1
            expected = 2
            obtained = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(expected - obtained) < eps*expected, \
                                "bad 1d maxmodnd %s" % (repr(obtained)))

    def test_maxmod_bivariate(self) :
        eps = 1e-9
        for C in classes :
            x, y = C.monomials(2, dtype=complex)
            p = (1 + x**9)*y**9 + 8
            expected = 10
            obtained = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(expected - obtained) < eps*expected, \
                                "bad 2d maxmodnd %s" % (repr(obtained)))

    def test_maxmod_kaijser_varopoulos(self) :
        # N. Varopoulos, On an inequality of von Neumann and an 
        # application of themetric theory of tensor products to 
        # operator theory, J. Funct. Anal., 16 (1974), 83--100.
        eps = 1e-5
        for C in classes :
            x, y, z = C.monomials(3, dtype=complex)
            p = x**2 + y**2 + z**2 - 2*x*y - 2*x*z - 2*y*z 
            expected = 5
            obtained = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(expected - obtained) < eps*expected, \
                                "bad kaijser-varopoulos maxmodnd %s" % \
                                (repr(obtained)))


class TestMVPolyIntd(unittest.TestCase) :

    def test_intd_bad_args(self) :
        for C in classes :
            x, y = C.monomials(2)
            p = x**2 + y + 1
            for iv in [[1], [1,2,3]] :
                self.assertRaises(AssertionError, p.intd, *iv)

    def test_intd_1d(self) :
        for C in classes :
            x, = C.monomials(1)
            p = x
            expected = 0.5
            for interval in [ [0, 1], 
                              (0, 1), 
                              np.array([0, 1]),
                              range(2) ] :
                obtained = p.intd(interval)
                self.assertTrue((expected == obtained).all(), \
                                    "bad integral %s" % (repr(obtained)))

    def test_intd_2d(self) :
        for C in classes :
            x, y = C.monomials(2)
            p = x**2 + 4*y
            expected = 1719
            obtained = p.intd([11, 14], [7, 10])
            self.assertTrue(expected == obtained, \
                                "bad integral %s" % (repr(obtained)))

    def test_intd_3d(self) :
        for C in classes :
            x, y, z = C.monomials(3)
            p = x + y + z
            expected = 1.5
            obtained = p.intd([0, 1], [0, 1], [0, 1])
            self.assertTrue(expected == obtained, \
                                "bad integral %s" % (repr(obtained)))
            p = 3*x**2 + y + z
            expected = 12
            obtained = p.intd([0, 1], [2, 4], [-2, 0])
            self.assertTrue(expected == obtained, \
                                "bad integral %s" % (repr(obtained)))

