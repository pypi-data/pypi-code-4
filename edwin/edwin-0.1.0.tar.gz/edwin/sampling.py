#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sampling.py --- Stochastic sampling algorithms

# Copyright (c) 2011, 2012, 2013  François Orieux <orieux@iap.fr>

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Commentary:

"""
References
----------
"""

# code:

from __future__ import division  # Then 10/3 provide 3.3333 instead of 3
import functools

import numpy as np
import numpy.random as npr

import optim

__author__ = "François Orieux"
__copyright__ = "Copyright (C) 2011, 2012, 2013 F. Orieux <orieux@iap.fr>"
__credits__ = ["François Orieux"]
__license__ = "mit"
__version__ = "0.1.0"
__maintainer__ = "François Orieux"
__email__ = "orieux@iap.fr"
__status__ = "development"
__url__ = ""
__keywords__ = "sampling algorithm, MCMC"


def po_draw_mdim_gauss(f_draw, f_transpose, f_hessian_proj, precisions, init,
                       cg_params=None):
    """Draw high-dimension gaussian law with PO algorithm

    This algorithm, described in [1], allow to draw (or simulate) very
    high-dimension law thanks to carefull use of optimisation
    algorithm.

    Parameters
    ----------
    f_draw : dict of callable
        Each items is a callable to draw a prior samples

    f_transpose : dict of callable
        Each items is a callable to compute the transpose of the prior
        samples.

    f_hessian_proj : callable
        Compute the hessian (or covariance) projection of a current
        space point. Used by the conjugate gradient.

    precisions : dict of float
        Same key than callable. They are the precision of gaussian
        prior models.

    init : array-like
        The initial value of the conjugate gradient

    cg_params : dict
        Conjugate gradient parameters. See ``optim``.

    Returns
    -------
    sample : array-like
        The gaussian sample

    References
    ----------
    .. [1] F. Orieux, O. Féron and J.-F. Giovannelli, "Sampling
       high-dimensional Gaussian distributions for general linear inverse
       problems", IEEE Signal Processing Letters, 2012

    See Acknowledgements section of the package ``README.rst`` to know
    how to add a citation.
    """
    if cg_params is None:
        cg_params = {}
    # Perturbation
    second_member = np.sum((2 * precisions[term] *
                            f_transpose[term](f_draw[term](precisions[term]))
                            for term in precisions.keys()),
                           axis=0)

    # Optimization
    sample, _, _ = optim.conj_grad(functools.partial(f_hessian_proj,
                                                     precisions),
                                   init, second_member, cg_params)

    return sample


def cdsampler(f_hessian_proj, init, second_member, params):
    """Conjugate direction sampler

    This function implement an algorithm to simulate a gaussian law by
    conjugate direction factorisation.
    """
    sample = init.copy()
    hess_proj = f_hessian_proj(sample)
    second_member = npr.standard_normal(hess_proj.shape)
    residual = second_member - hess_proj
    direction = residual.copy()

    for iteration in range(min(init.size, params["max_iter"])):
        hess_proj = f_hessian_proj(direction)
        variance = np.sum(hess_proj * direction)
        eee = np.sum(hess_proj * sample) / variance
        fff = np.sum(direction * hess_proj) / variance
        zzz = npr.standard_normal((1, ))
        coef = zzz / np.sqrt(variance)
        sample += (coef - eee) * direction
        second_member += (coef - fff) * hess_proj
        residual -= (fff - eee) * hess_proj
        direction = residual - np.sum(residual *
                                      hess_proj) * direction / variance

    return (sample, second_member)
