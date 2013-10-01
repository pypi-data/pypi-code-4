#!/usr/bin/env python
# -*- coding: utf-8 -*-
# optim.py --- Optimisation algorithm

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

"""Numerical optimisation algorithms

These modules implements personnal designed classical optimisation
algorithm like linear conjugate gradient, with or without
preconditionner.

I have implemented these algorithms:
- to be adapted to large inverse problems with high-dimension unknown
  (>1e6)
- for learning
- to not depends on another package.

References
----------
.. [1] J. R. Shewchuk, "An introduction to the Conjugate Gradient
   Method without the Agonizing Pain", report, 1994
"""

# code:

from __future__ import division  # Then 10/3 provide 3.3333 instead of 3
import time
import warnings

import numpy as np

__author__ = "François Orieux"
__copyright__ = "Copyright (C) 2011, 2012, 2013 F. Orieux <orieux@iap.fr>"
__credits__ = ["François Orieux"]
__license__ = "mit"
__version__ = "0.1.0"
__maintainer__ = "François Orieux"
__email__ = "orieux@iap.fr"
__status__ = "development"
__url__ = ""
__keywords__ = "numerical optimisation, linear conjuage gradient"


def conj_grad(f_hessian_proj, init, second_term, user_params=None):
    """Linear conjugate gradient

    This function compute the solution of a linear system `Ax = b`
    with a iterative conjugated gradient algorithm. This function is
    specially usefull for problems in great dimension. This algorithm
    is compatible with variable in *complex* unknowns.

    Parameters
    ----------
    f_hessian_proj : callable (function-like)
        The callable object to compute the product `Ax`. The signature
        must accept only on parameter `x`.

    init : array_like
        The starting point of the algorithm

    second_term : array_like
        The second term `b` of the system

    Other parameters
    ----------------
    user_params : dict, optional
        The dictionnary of parameters for the conjugate gradient
        algorithm. The lookup key are
        - 'min_iter' and 'max_iter' for the minumun and maximum
          iteration (10 and 50 by default)
        - 'f_crit' for a callable to compute the criterion value at
          current iteration (None by default)
        - 'threshold' as the ration between initial and final residual
          norm, as a stoping criterion (1e-5 by default)
        - 'restart' is the frequency in iteration for restarting the
          CG to remove accumulation of numerical error roundoff.

    Returns
    -------
    minimizer : array_like
        The minimum `x` found to satisfy `Ax = b`
    cg_info : dict
        Information about the algorithm. `residual_norm` is a list of
        residual norm at each iteration. `loop_time` is a list of
        current time at the end of each iteration. `crit_val` is set
        if `f_crit` function is provided in user_params.
    state : string
        A string describing the condition to the stop.

    See Also
    --------
    pcg, binsch

    References
    ----------
    .. [1] J. R. Shewchuk, "An introduction to the Conjugate Gradient
       Method without the Agonizing Pain", report, 1994
    """
    params = {'threshold': 1e-5, 'max_iter': 50, 'min_iter': 10,
              'f_crit': None, 'restart': 50}
    params.update(user_params if user_params else {})

    if params['min_iter'] > params['max_iter']:
        warnings.warn("Maximum iteration ({0}) is lower than"
                      " minimum iteration ({1}). "
                      "Maximum is set to mininum".format(params['max_iter'],
                                                         params['min_iter']))
        params['max_iter'] = params['min_iter']

    # Gradient at current init
    residual = second_term - f_hessian_proj(init)
    descent = residual

    minimizer = init

    cg_info = {'residual_norm': [np.sum(np.abs(residual)**2)],
               'loop_time': [time.time()]}

    for iteration in range(init.size):
        if iteration >= params['max_iter']:
            return (minimizer, cg_info, 'End by iteration')

        hess_proj = f_hessian_proj(descent)
        # a = r^tr/d^tAd
        # Optimal step in direction of descent
        step = cg_info['residual_norm'][-1] / np.sum(np.real(np.conj(descent) *
                                                             hess_proj))

        # Descent x^(i+1) = x^(i) + ad
        minimizer = minimizer + step * descent  # not += because
                                                 # there is a bug with
                                                 # numpy (=1.4)

        # r^(i+1) = r^(i) - a*Ad
        if (iteration % params['restart']) == 0:
            residual = second_term - f_hessian_proj(minimizer)
        else:
            residual = residual - step * hess_proj

        # Conjugate direction
        cg_info['residual_norm'].append(np.sum(np.abs(residual)**2))
        beta = cg_info['residual_norm'][-1] / cg_info['residual_norm'][-2]
        descent = residual + beta * descent

        if params['f_crit']:
            cg_info['crit_val'].append(params['f_crit'](minimizer))
        cg_info['loop_time'].append(time.time())

        # Stopping criterion
        if (iteration > params['min_iter']) and (cg_info['residual_norm'][-1] <
                                                 params['threshold'] *
                                                 cg_info['residual_norm'][0]):
            return (minimizer, cg_info, 'End by criterion')

    return (minimizer, cg_info, 'All direction optimized')


def pcg(f_hessian_proj, init, second_term, f_precond, user_params=None):
    """Linear preconditionned conjugate gradient

    This function compute the solution of a linear system `Ax = b`
    with a iterative precondionned conjugated gradient algorithm. This
    function is specially usefull for problems in great
    dimension. This algorithm is compatible with variable in complex
    numbers.

    Parameters
    ----------
    f_hessian_proj : callable
        The callable object to compute the product `Ax`. The signature
        must accept only on parameter `x`.

    init : array_like
        The starting point of the algorithm

    second_term : array_like
        The second term `b` of the system

    f_precond : callable, function_like
        The callable object to compute the application of the
        preconditionner `M`. The signature must accept only on
        parameter `x`.

    Other parameters
    ----------------
    user_params : dict, optional
        The dictionnary of parameters for the conjugate gradient
        algorithm. The lookup keyword are
        - 'min_iter' and 'max_iter' for the minumun and maximum
          iteration (10 and 50 by default)
        - 'f_crit' for a callable to compute the criterion value at
          current iteration (None by default)
        - 'threshold' as the ration between initial and final residual
          norm, as a stoping criterion (1e-5 by default)
        - 'restart' is the frequency in iteration for restarting the
          CG to remove accumulation of numerical error roundoff.

    Returns
    -------
    minimizer : array_like
        The minimum `x` found to satisfy `Ax = b`

    cg_info : dict
        Information about the algorithm. 'residual_norm' is a list of
        residual norm at each iteration. 'loop_time' is a list of
        current time at the end of each iteration. 'crit_val' is set
        if 'f_crit' function is provided in user_params.

    state : string
        A string describing the condition to the stop.

    See Also
    --------
    cg, binsch

    References
    ----------
    .. [1] J. R. Shewchuk, "An introduction to the Conjugate Gradient
       Method without the Agonizing Pain", report, 1994
    """
    params = {'threshold': 1e-5, 'max_iter': 50, 'min_iter': 10,
              'f_crit': None, 'restart': 50}
    params.update(user_params if user_params else {})

    if params['min_iter'] > params['max_iter']:
        warnings.warn("Minimum iteration ({0}) is lower than"
                      " maximum iteration ({1}). "
                      "Maximum is set to mininum".format(params['min_iter'],
                                                         params['max_iter']))
        params['max_iter'] = params['min_iter']

    # Gradient at current init
    residual = second_term - f_hessian_proj(init)
    descent = f_precond(residual)

    minimizer = init

    cg_info = {'residual_norm': [np.sum(np.real(np.conj(residual) *
                                                descent))],
               'loop_time': [time.time()]}

    for iteration in range(init.size):
        hess_proj = f_hessian_proj(descent)
        # a = r^tr/d^tAd
        # Optimal step in direction of descent
        step = cg_info['residual_norm'][-1] / np.sum(np.real(np.conj(descent) *
                                                             hess_proj))

        # Descent x^(i+1) = x^(i) + ad
        minimizer = minimizer + step * descent  # not += because
                                                 # there is a bug with
                                                 # numpy (=1.4)

        # r^(i+1) = r^(i) - a*Ad (think residual as gradient in data space)
        if (iteration % params['restart']) == 0:
            residual = second_term - f_hessian_proj(minimizer)
        else:
            residual = residual - step * hess_proj

        # Conjugate direction with preconditionner
        secant = f_precond(residual)
        cg_info['residual_norm'].append(np.sum(np.real(np.conj(residual)
                                                       * secant)))
        beta = cg_info['residual_norm'][-1] / cg_info['residual_norm'][-2]
        descent = secant + beta * descent

        if params['f_crit']:
            cg_info['crit_val'].append(params['f_crit'](minimizer))
        cg_info['loop_time'].append(time.time())

        # Stopping criterion
        if (iteration > params['min_iter']) and (cg_info['residual_norm'][-1] <
                                                 params['threshold'] *
                                                 cg_info['residual_norm'][0]):
            return (minimizer, cg_info, 'End by criterion')

        if iteration >= params['max_iter']:
            return (minimizer, cg_info, 'End by iteration')

    return (minimizer, cg_info, 'All direction optimized')


def binsch(crit, interval, epsilon=1e-7, iteration=100):
    """Bisection of scalar cost function
    """
    lower_bound = np.min(interval)
    upper_bound = np.max(interval)
    half_bound = (lower_bound + upper_bound) / 2

    xaxis = [lower_bound, half_bound, upper_bound]

    val_lower_bound = crit(lower_bound)
    val_upper_bound = crit(upper_bound)
    val_half_bound = crit(half_bound)

    yaxis = [val_lower_bound, val_half_bound, val_upper_bound]

    while ((np.abs(upper_bound - lower_bound) >=
            epsilon) and (iteration >= 1)):
        quart_bound = (lower_bound + half_bound) / 2
        three_quart_bound = (half_bound + upper_bound) / 2

        xaxis.append(quart_bound)
        xaxis.append(three_quart_bound)

        val_quart_bound = crit(quart_bound)
        val_three_quart_bound = crit(three_quart_bound)

        yaxis.append(val_quart_bound)
        yaxis.append(val_three_quart_bound)

        argmin = np.argmin([val_lower_bound, val_quart_bound,
                            val_half_bound,
                            val_three_quart_bound, val_upper_bound])

        if (argmin == 1) or (argmin == 2):
            # If the min is lower_bound or quart_bound
            upper_bound = half_bound
            half_bound = quart_bound
            val_upper_bound = val_half_bound
            val_half_bound = val_quart_bound
        elif argmin == 3:
            # If the min is half_bound
            lower_bound = quart_bound
            upper_bound = three_quart_bound
            val_lower_bound = val_quart_bound
            val_upper_bound = val_three_quart_bound
        else:
            # If the min is three_quart_bound or upper_bound
            lower_bound = half_bound
            half_bound = three_quart_bound
            val_lower_bound = val_half_bound
            val_half_bound = val_three_quart_bound

        iteration -= 1

    xaxis = np.sort(xaxis)
    yaxis = np.array(yaxis)[np.argsort(xaxis)]

    return ([lower_bound, upper_bound], xaxis, yaxis)
