import unittest

import numpy

from .. import core


class TestEarth(unittest.TestCase):
    def assertAllClose(self, a, b, rtol=1e-05, atol=1e-08):
        if numpy.allclose(a, b, rtol, atol):
            return
        else:
            self.fail("%s != %s to within tolerance" % (a, b))

    def test_forward(self):
        x = numpy.linspace(0, 1, num=100, endpoint=True)
        y = numpy.hstack((numpy.zeros(50), (x[50:] - 0.5)))

        n, best_set, bx, dirs, cuts = \
            core.forward_pass(x.reshape(-1, 1), y, degree=1, terms=3,
                               penalty=0, new_var_penalty=0)

        self.assertEqual(n, 3)
        self.assertTrue((best_set == [True, True, True]).all())

        self.assertTrue(numpy.allclose(cuts.ravel(),
                                       [0, 0.5, 0.5], atol=0.05))

        self.assertTrue((dirs.ravel() == [0, 1, -1]).all())

        # raise y by 1.0 and repeat
        y += 1.0

        n, best_set, bx, dirs, cuts = \
            core.forward_pass(x.reshape(-1, 1), y, degree=1, terms=3,
                               penalty=0, new_var_penalty=0)

        self.assertEqual(n, 3)
        self.assertTrue((best_set == [True, True, True]).all())

        self.assertTrue(numpy.allclose(cuts.ravel(),
                                       [0, 0.5, 0.5], atol=0.05))

        self.assertTrue((dirs.ravel() == [0, 1, -1]).all())

    def test_base_transform(self):
        X = [[1., 2., 3.],
             [0., 5., 10.]]

        # H(X[0] - 0.5) * H(7 - X[2])
        cuts = [0.5, 3., 7.]
        dirs = [1, 0, -1]

        bX = core.base_term_transform(X, cuts, dirs)
        self.assertAllClose(bX, [[2.], [0.]])

        cuts = [[0, 0, 0], cuts]
        dirs = [[0, 0, 0], dirs]

        bX = core.base_term_transform(X, cuts, dirs)
        self.assertAllClose(bX, [[0., 2.], [0., 0.]])

        bX = core.base_term_transform(X, cuts, dirs, intercept=True)
        self.assertAllClose(bX, [[1., 2.], [1., 0.]])
