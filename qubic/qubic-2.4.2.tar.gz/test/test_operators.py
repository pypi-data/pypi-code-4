from __future__ import division

import healpy as hp
import numpy as np
from numpy import radians as r
from numpy.testing import assert_allclose
from qubic.operators import (
    DirectionHealpix2CartesianOperator, DirectionCartesian2HealpixOperator,
    DirectionHealpix2SphericalOperator, DirectionSpherical2HealpixOperator,
    DirectionCartesian2SphericalOperator, DirectionSpherical2CartesianOperator)

nside = 16
pixs = (2, [2, 4, 8], [[2, 3, 5], [10, 6, 8]])
vecs = ([1, 0, 0], [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
         [[1, 0, 0], [0, 1, 0], [0, 0, 1]]])
angs = ([r(10), r(5)], [[r(9), r(3)], [r(8), r(2)], [r(7), r(1)]],
        [[[r(9), r(3)], [r(8), r(2)], [r(8), r(2)]],
         [[r(7), r(3)], [r(7), r(1)], [r(6), r(4)]]])
hps = hp.pix2vec, hp.vec2pix, hp.pix2ang, hp.ang2pix
clss = (DirectionHealpix2CartesianOperator, DirectionCartesian2HealpixOperator,
        DirectionHealpix2SphericalOperator, DirectionSpherical2HealpixOperator)
inputs = pixs, vecs, pixs, angs
nins = 1, 3, 1, 2
nouts = 3, 1, 2, 1


def test_directions():
    def _get_input(n, x):
        if n == 1:
            return (x,)
        elif n == 2:
            return (x[..., 0], x[..., 1])
        elif n == 3:
            return (x[..., 0], x[..., 1], x[..., 2])

    def _get_output(n, args):
        if n == 1:
            return args
        else:
            a = np.array(args)
            return np.rollaxis(a, axis=0, start=a.ndim)

    def func(nest, h, c, i, nin, nout):
        i = np.array(i)
        op = c(nside, nest=nest)
        actual = op(i)
        i2 = _get_input(nin, i)
        expected = _get_output(nout, h(nside, *i2, nest=nest))
        assert_allclose(actual, expected)

    for nest in (True, False):
        for h, c, ii, nin, nout in zip(hps, clss, inputs, nins, nouts):
            for i in ii:
                yield func, nest, h, c, i, nin, nout


def test_sphvec1():
    vec = vecs[1]
    expected = np.radians([[90, 0], [90, 90], [0, 0]])

    def func(v, e):
        vec2ang = DirectionCartesian2SphericalOperator()
        assert_allclose(vec2ang(v), e)

    for v, e in zip(vec, expected):
        yield func, v, e


def test_sphvec2():
    vec2ang = DirectionCartesian2SphericalOperator()
    ang2vec = DirectionSpherical2CartesianOperator()

    def func(v):
        assert_allclose(ang2vec(vec2ang(v)), v, atol=1e-15)

    for v in vecs:
        yield func, v
