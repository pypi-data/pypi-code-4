import logging
import unittest

from nose.plugins.attrib import attr

import numpy as np

from empirical.interpolate import (
    lagrange_diffs,
    lagrange,
    lagrange_2D,
    lagrange_2D_a,
    lagrange_polys_2D,
    Newton,
)
from empirical.quadrature import (
    gauss,
    clenshaw_curtis,
    legendre_gauss_lobatto,
)


log = logging.getLogger(__name__)


class InterpolateTest(unittest.TestCase):

    def test_lagrange(self):
        test_points = np.linspace(-1, 1, 500)

        for N in [10, 15, 20, 25, 30]:
            for x in [legendre_gauss_lobatto(N)[0], clenshaw_curtis(N)[0],
                      gauss(N)[0]]:
                diffs = lagrange_diffs(x)
                for f in [lambda x: np.sin(x), lambda x: np.cos(x),
                          lambda x: 3 + 2 * x + 8 * x ** 2 + 5 * x ** 8]:
                    evals = f(x)
                    expected = f(test_points)
                    actual = lagrange(x, diffs, evals, test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)

    @attr('slow')
    def test_lagrange_2D(self):
        test_points = np.linspace(-1, 1, 50)
        test_points_x, test_points_y = np.meshgrid(test_points, test_points)
        test_points = np.empty((test_points_x.shape[0],
                                test_points_y.shape[1],
                                2))
        test_points[:, :, 0] = test_points_x
        test_points[:, :, 1] = test_points_y

        for N, M in [(15, 15), (15, 20), (20, 15)]:
            for x in [legendre_gauss_lobatto(N)[0], clenshaw_curtis(N)[0],
                      gauss(N)[0]]:
                diffs_x = lagrange_diffs(x)
                for y in [legendre_gauss_lobatto(M)[0],
                          clenshaw_curtis(M)[0], gauss(M)[0]]:
                    diffs_y = lagrange_diffs(y)
                    for f in [lambda x, y: np.sin(x) * np.cos(y),
                              lambda x, y: x * y + x ** 5 - y ** 3]:
                        evals = f(test_points_x, test_points_y)
                        expected = f(test_points_x, test_points_y)
                        actual = lagrange_2D(x, y, diffs_x, diffs_y, evals,
                                             test_points)
                        log.debug(expected - actual)
                        self.assertLessEqual(
                            np.amax(np.abs(expected - actual)), 1e-8)

    @attr('slow')
    def test_lagrange_2D_a(self):
        test_points = np.linspace(-1, 1, 50)
        test_points_x, test_points_y = np.meshgrid(test_points, test_points)
        test_points = np.empty((test_points_x.shape[0],
                                test_points_y.shape[1],
                                2))
        test_points[:, :, 0] = test_points_x
        test_points[:, :, 1] = test_points_y

        for N, M in [(15, 15), (15, 20), (20, 15)]:
            for x in [legendre_gauss_lobatto(N)[0], clenshaw_curtis(N)[0],
                      gauss(N)[0]]:
                for y in [legendre_gauss_lobatto(M)[0],
                          clenshaw_curtis(M)[0], gauss(M)[0]]:
                    polys = lagrange_polys_2D(x, y)
                    for f in [lambda x, y: np.sin(x) * np.cos(y),
                              lambda x, y: x * y + x ** 5 - y ** 3]:
                        evals = f(test_points_x, test_points_y)
                        expected = f(test_points_x, test_points_y)
                        actual = lagrange_2D_a(polys, evals, test_points)
                        log.debug(expected - actual)
                        self.assertLessEqual(
                            np.amax(np.abs(expected - actual)), 1e-8)

    def test_newton(self):
        test_points = np.linspace(-1, 1, 500)

        for N in [10, 15, 20, 25, 30]:
            for x in [np.linspace(-1, 1, N), legendre_gauss_lobatto(N)[0],
                      clenshaw_curtis(N)[0], gauss(N)[0]]:
                for f in [lambda x: np.sin(x), lambda x: np.cos(x),
                          lambda x: 3 + 2 * x + 8 * x ** 2 + 5 * x ** 8]:
                    y = f(x)
                    interp = Newton(x, y)
                    expected = f(test_points)
                    actual = interp(test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)
