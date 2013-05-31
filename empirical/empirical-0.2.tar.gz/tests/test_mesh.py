import unittest

import numpy as np

from empirical.mesh import (
    Mesh1D,
    Mesh2D,
)
from empirical.quadrature import (
    gauss,
    legendre_gauss_lobatto,
)


class Mesh1DTest(unittest.TestCase):

    def assert_a_b(self, mesh, a, b):
        self.assertEqual(mesh.a, a)
        self.assertEqual(mesh.b, b)
        self.assertAlmostEqual(mesh.x[0], a, places=10)
        self.assertAlmostEqual(mesh.vector[0, 0], a, places=10)
        self.assertAlmostEqual(mesh.grid[0, 0], a, places=10)
        self.assertAlmostEqual(mesh.x[-1], b, places=10)
        self.assertAlmostEqual(mesh.vector[-1, 0], b, places=10)
        self.assertAlmostEqual(mesh.grid[-1, 0], b, places=10)

    def assert_size(self, mesh, N):
        self.assertEqual(mesh.N, N)
        self.assertEqual(mesh.x.shape, (N,))
        self.assertEqual(mesh.w.shape, (N,))
        self.assertEqual(mesh.vector.shape, (N, 1))
        self.assertEqual(mesh.vector_weights.shape, (N, 1))
        self.assertEqual(mesh.grid.shape, (N, 1))
        self.assertEqual(mesh.grid_weights.shape, (N, 1))

    def test_constructor(self):
        a, b = -1, 1
        mesh = Mesh1D(a, b)
        self.assert_a_b(mesh, a, b)

        a, b = -0.5, 3.3
        mesh = Mesh1D(a, b)
        self.assert_a_b(mesh, a, b)

        a, b = 0.4, -2
        mesh = Mesh1D(a, b)
        self.assert_a_b(mesh, a, b)

    def test_recalc_quadrature(self):
        N = 20
        mesh = Mesh1D(-1, 1, N)

        # Test that the size is properly changed.
        self.assert_size(mesh, N)
        N = 35
        mesh.recalc_quadrature(N)
        self.assert_size(mesh, N)

        # Test that the 'qtype' keyword works
        qtype = 'lgl'
        mesh.recalc_quadrature(qtype=qtype)
        self.assert_size(mesh, N)
        self.assertEqual(mesh.qtype, qtype)
        self.assertEqual(mesh.quadrule, legendre_gauss_lobatto)

        # Test that the 'quadrule' keyword works
        quadrule = legendre_gauss_lobatto
        mesh.recalc_quadrature(qtype=None, quadrule=quadrule)
        self.assert_size(mesh, N)
        self.assertIsNone(mesh.qtype)
        self.assertEqual(mesh.quadrule, legendre_gauss_lobatto)

    
class Mesh2DTest(unittest.TestCase):

    def assert_a_b(self, mesh, a_x, b_x, a_y, b_y):
        self.assertEqual(mesh.a_x, a_x)
        self.assertEqual(mesh.b_x, b_x)
        self.assertEqual(mesh.a_y, a_y)
        self.assertEqual(mesh.b_y, b_y)
        self.assertAlmostEqual(mesh.x[0], a_x, places=10)
        self.assertAlmostEqual(mesh.y[0], a_y, places=10)
        self.assertAlmostEqual(mesh.vector[0, 0], a_x, places=10)
        self.assertAlmostEqual(mesh.vector[0, 1], a_y, places=10)
        self.assertAlmostEqual(mesh.grid[0, 0, 0], a_x, places=10)
        self.assertAlmostEqual(mesh.grid[0, 0, 1], a_y, places=10)
        self.assertAlmostEqual(mesh.x[-1], b_x, places=10)
        self.assertAlmostEqual(mesh.y[-1], b_y, places=10)
        self.assertAlmostEqual(mesh.vector[-1, 0], b_x, places=10)
        self.assertAlmostEqual(mesh.vector[-1, 1], b_y, places=10)
        self.assertAlmostEqual(mesh.grid[-1, -1, 0], b_x, places=10)
        self.assertAlmostEqual(mesh.grid[-1, -1, 1], b_y, places=10)

    def assert_size(self, mesh, N, M):
        self.assertEqual(mesh.N, N)
        self.assertEqual(mesh.M, M)
        self.assertEqual(mesh.x.shape, (N,))
        self.assertEqual(mesh.y.shape, (M,))
        self.assertEqual(mesh.w_x.shape, (N,))
        self.assertEqual(mesh.w_y.shape, (M,))
        self.assertEqual(mesh.vector.shape, (N * M, 2))
        self.assertEqual(mesh.vector_weights.shape, (N * M,))
        self.assertEqual(mesh.grid.shape, (M, N, 2))
        self.assertEqual(mesh.grid_weights.shape, (M, N,))

    def test_constructor(self):
        a_x, b_x, a_y, b_y = -1, 1, -1, 1
        mesh = Mesh2D(a_x, b_x, a_y, b_y)
        self.assert_a_b(mesh, a_x, b_x, a_y, b_y)

        a_x, b_x, a_y, b_y = -0.5, 3.3, 2.2, 4.5
        mesh = Mesh2D(a_x, b_x, a_y, b_y)
        self.assert_a_b(mesh, a_x, b_x, a_y, b_y)

        a_x, b_x, a_y, b_y = 0.4, -2, 0.3, -1.5
        mesh = Mesh2D(a_x, b_x, a_y, b_y)
        self.assert_a_b(mesh, a_x, b_x, a_y, b_y)

    def test_recalc_quadrature(self):
        N, M = 20, 20
        mesh = Mesh2D(-1, 1, -1, 1, N, M)

        # Test that the size is properly changed.
        self.assert_size(mesh, N, M)
        N, M = 35, 40
        mesh.recalc_quadrature(N, M)
        self.assert_size(mesh, N, M)

        # Test that the 'qtype' keyword works
        qtype_x = 'lgl'
        qtype_y = 'gauss'
        mesh.recalc_quadrature(qtype_x=qtype_x, qtype_y=qtype_y)
        self.assert_size(mesh, N, M)
        self.assertEqual(mesh.qtype_x, qtype_x)
        self.assertEqual(mesh.qtype_y, qtype_y)
        self.assertEqual(mesh.quadrule_x, legendre_gauss_lobatto)
        self.assertEqual(mesh.quadrule_y, gauss)

        # Test that the 'quadrule' keyword works
        quadrule_x = gauss
        quadrule_y = legendre_gauss_lobatto
        mesh.recalc_quadrature(quadrule_x=quadrule_x,
                               quadrule_y=quadrule_y)
        self.assert_size(mesh, N, M)
        self.assertIsNone(mesh.qtype_x)
        self.assertIsNone(mesh.qtype_y)
        self.assertEqual(mesh.quadrule_x, gauss)
        self.assertEqual(mesh.quadrule_y, legendre_gauss_lobatto)
