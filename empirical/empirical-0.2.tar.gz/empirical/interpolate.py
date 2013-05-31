__all__ = [
    "lagrange_diffs",
    "lagrange_multiplier",
    "lagrange",
    "lagrange_2D",
    "lagrange_polys_2D",
    "lagrange_2D_a",
    "Newton",
]

import logging

import numpy as np

from sympy import Symbol
from sympy.utilities.autowrap import ufuncify


log = logging.getLogger(__name__)


def lagrange_diffs(nodes):
    diffs = np.empty((nodes.size, nodes.size))
    for i in range(nodes.size):
        diffs[i, :] = nodes[i] - nodes
    return diffs


def lagrange_multiplier(nodes, diffs, i, x):
    ans = np.ones_like(x)
    for j in range(nodes.size):
        if i == j:
            continue
        ans *= (x - nodes[j]) / diffs[i, j]
    return ans


def lagrange(nodes, diffs, evals, points):
    ans = np.zeros_like(points, dtype=evals.dtype)
    for i in range(nodes.size):
        ans += evals[i] * lagrange_multiplier(nodes, diffs, i, points)
    return ans


def lagrange_polys_2D(nodes_x, nodes_y):
    nodes_x = np.asarray(nodes_x)
    nodes_y = np.asarray(nodes_y)
    x = Symbol('x')
    polys_x = []
    for i in range(nodes_x.size):
        poly = 0
        for j in range(nodes_x.size):
            if i == j:
                continue
            poly += (x - nodes_x[j]) / (nodes_x[i] - nodes_x[j])
        polys_x += [ufuncify(x, poly)]
    polys_y = []
    for i in range(nodes_y.size):
        poly = 0
        for j in range(nodes_y.size):
            if i == j:
                continue
            poly += (x - nodes_y[j]) / (nodes_y[i] - nodes_y[j])
        polys_y += [ufuncify(x, poly)]
    return (polys_x, polys_y)


def lagrange_2D_a(polys, evals, points):
    points = np.asarray(points)
    polys_x, polys_y = polys
    ans = np.zeros(points.shape[:-1], dtype=points.dtype)
    for i in range(evals.shape[1]):
        for j in range(evals.shape[0]):
            ans += (evals[j, i] *
                    polys_x[i](points[..., 0]).reshape(points.shape[:-1]) *
                    polys_y[j](points[..., 1]).reshape(points.shape[:-1]))
    return ans


def lagrange_2D(nodes_x, nodes_y, diffs_x, diffs_y, evals, points):
    points = np.asarray(points)
    ans = np.zeros(points.shape[:-1], dtype=points.dtype)
    for i in range(nodes_x.size):
        for j in range(nodes_y.size):
            ans += (evals[j, i] *
                    lagrange_multiplier(nodes_x, diffs_x, i, points[..., 0]) *
                    lagrange_multiplier(nodes_y, diffs_y, j, points[..., 1]))
    return ans

class Newton:

    def __init__(self, nodes, evals):
        self.nodes = nodes
        self.evals = evals
        self.N = self.nodes.size
        self.a = np.copy(evals)
        for j in range(1, self.N):
            for i in range(self.N - 1, j - 1, -1):
                self.a[i] = ((self.a[i] - self.a[i-1]) /
                             (nodes[i] - nodes[i - j]))

    def __call__(self, x):
        ans = np.ones_like(x) * self.a[-1]
        for i in range(self.N - 2, -1, -1):
            ans = ans * (x - self.nodes[i]) + self.a[i]
        return ans
