__all__ = [
    "Mesh1D",
    "Mesh2D",
]

import logging

import numpy as np

from scipy.interpolate import interp1d, RectBivariateSpline

from empirical.quadrature import (
    get_quadrature,
    transform_nodes,
)


log = logging.getLogger(__name__)


class Mesh1D:

    def __init__(self, a, b, N=20, qtype='linear', quadrule=None):
        self.a = a
        self.b = b
        self.N = N
        self.qtype = qtype
        self.quadrule = quadrule

        self.recalc_quadrature(N=N, qtype=qtype, quadrule=quadrule)

    def recalc_quadrature(self, N=None, qtype=None, quadrule=None):
        if N is None:
            N = self.N
        self.N = N
        self.qtype, self.quadrule = get_quadrature(qtype, quadrule, self.qtype,
                                                   self.quadrule)
        # We actually do want to define new variables here:
        # pylint: disable=W0201
        self.x, self.w = self.quadrule(N)
        transform_nodes(self.a, self.b, self.x)

        self.vector = self.x.reshape((self.x.size, 1))
        self.vector_weights = self.w.reshape((self.w.size, 1))
        self.grid = self.vector
        self.grid_weights = self.vector_weights

    def interpolate_func(self, evals, kind='cubic', copy=False, **kwargs):
        return interp1d(self.x, evals, kind=kind, copy=copy, **kwargs)


class Mesh2D:

    def __init__(self, a_x, b_x, a_y, b_y, N=20, M=20,
                 qtype_x='linear', quadrule_x=None,
                 qtype_y='linear', quadrule_y=None):
        self.a_x = a_x
        self.b_x = b_x
        self.a_y = a_y
        self.b_y = b_y
        self.N = N
        self.M = M
        self.qtype_x = qtype_x
        self.quadrule_x = quadrule_x
        self.qtype_y = qtype_y
        self.quadrule_y = quadrule_y

        self.recalc_quadrature(N, M, qtype_x, quadrule_x, qtype_y, quadrule_y)

    def recalc_quadrature(self, N=None, M=None, qtype_x=None, quadrule_x=None,
                          qtype_y=None, quadrule_y=None):
        if N is None:
            N = self.N
        if M is None:
            M = self.M
        self.N = N
        self.M = M
        self.qtype_x, self.quadrule_x = get_quadrature(qtype_x, quadrule_x,
                                                       self.qtype_x,
                                                       self.quadrule_x)
        self.qtype_y, self.quadrule_y = get_quadrature(qtype_y, quadrule_y,
                                                       self.qtype_y,
                                                       self.quadrule_y)
        # We actually do want to define new variables here:
        # pylint: disable=W0201
        self.x, self.w_x = self.quadrule_x(N)
        self.y, self.w_y = self.quadrule_y(M)
        transform_nodes(self.a_x, self.b_x, self.x)
        transform_nodes(self.a_y, self.b_y, self.y)

        xx, yy = np.meshgrid(self.x, self.y)
        wxx, wyy = np.meshgrid(self.w_x, self.w_y)

        self.grid = np.empty((xx.shape[0], xx.shape[1], 2))
        self.grid[:, :, 0] = xx
        self.grid[:, :, 1] = yy
        self.grid_weights = wxx * wyy
        self.vector = np.empty((xx.size, 2), dtype=xx.dtype)
        self.vector[:, 0] = xx.reshape(xx.size)
        self.vector[:, 1] = yy.reshape(yy.size)
        self.vector_weights = wxx.reshape(wxx.size) * wyy.reshape(wyy.size)

    def interpolate_func(self, evals, kx=3, ky=3, **kwargs):
        x = self.x
        y = self.y
        z = evals.reshape(self.grid_weights.shape).transpose()
        return RectBivariateSpline(x, y, z, kx=kx, ky=ky, **kwargs)
