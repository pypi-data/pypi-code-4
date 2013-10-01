#!/usr/bin/env python
# -*- coding: utf-8 -*-
# improcessing.py --- Image processing

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

"""This module implements function for image processing. The most
important function is actually udeconv that implement an unsupervised
deconvolution described in [1]. Add a citation if you use this work
and see Acknowledgements section in the package ``README.rst``.

.. [1] François Orieux, Jean-François Giovannelli, and Thomas
       Rodet, "Bayesian estimation of regularization and point
       spread function parameters for Wiener-Hunt deconvolution",
       J. Opt. Soc. Am. A 27, 1593-1607 (2010)

http://www.opticsinfobase.org/josaa/abstract.cfm?URI=josaa-27-7-1593

"""

# code:

from __future__ import division  # Then 10/3 provide 3.3333 instead of 3

import numpy as np
import numpy.random as npr

from otb import uft

__author__ = "François Orieux"
__copyright__ = "Copyright (C) 2011, 2012, 2013 F. Orieux <orieux@iap.fr>"
__credits__ = ["François Orieux"]
__license__ = "mit"
__version__ = "0.1.0"
__maintainer__ = "François Orieux"
__email__ = "orieux@iap.fr"
__status__ = "development"
__url__ = ""
__keywords__ = "image processing, deconvolution"


def deconv(data, imp_resp, reg_val, reg=None, real=True):
    """Wiener-Hunt deconvolution

    return the deconvolution with a wiener-hunt approach (ie with
    Fourier diagonalisation).

    Parameters
    ----------
    data : ndarray
       The data

    imp_resp : ndarray
       The impulsionnal response in real space or the transfer
       function. Differentiation is done with the dtype where
       transfer function is supposed complex.

    reg_val : float
       The regularisation parameter value.

    reg : ndarray, optional
       The regularisation operator. The laplacian by
       default. Otherwise, the same constraints that for `imp_resp`
       apply

    real : boolean, optional
       True by default. Specify if `imp_resp` or `reg` are provided
       with hermitian hypothesis or not. See otb.uft module.

    Returns
    -------
    im_deconv : ndarray
       The deconvolued data

    References
    ----------
    .. [1] François Orieux, Jean-François Giovannelli, and Thomas
           Rodet, "Bayesian estimation of regularization and point
           spread function parameters for Wiener-Hunt deconvolution",
           J. Opt. Soc. Am. A 27, 1593-1607 (2010)

           http://www.opticsinfobase.org/josaa/abstract.cfm?URI=josaa-27-7-1593

       [2] B. R. Hunt "A matrix theory proof of the discrete
           convolution theorem", IEEE Trans. on Audio and
           Electroacoustics, vol. au-19, no. 4, pp. 285-288, dec. 1971
    """
    if not reg:
        reg, _ = uft.laplacian(data.ndim, data.shape)
    if reg.dtype != np.complex:
        reg = uft.ir2tf(reg, data.shape)

    if imp_resp.shape != reg.shape:
        trans_func = uft.ir2tf(imp_resp, data.shape)
    else:
        trans_func = imp_resp

    wiener_filter = np.conj(trans_func) / (np.abs(trans_func)**2 +
                                           reg_val * np.abs(reg)**2)
    if real:
        return uft.uirfft2(wiener_filter * uft.urfft2(data))
    else:
        return uft.uifft2(wiener_filter * uft.ufft2(data))


def udeconv(data, imp_resp, reg=None, user_params={}):
    """Unsupervised Wiener-Hunt deconvolution

    return the deconvolution with a wiener-hunt approach, where the
    hyperparameters are estimated (or automatically tuned from a
    practical point of view). The algorithm is a stochastic iterative
    process (Gibbs sampler).

    This work can be free software. If you use this work add a
    citation to the reference below.

    Parameters
    ----------
    data : ndarray
       The data

    imp_resp : ndarray
       The impulsionnal response in real space or the transfer
       function. Differentiation is done with the dtype where
       transfer function is supposed complex.

    reg : ndarray, optional
       The regularisation operator. The laplacian by
       default. Otherwise, the same constraints that for `imp_resp`
       apply

    user_params : dict
       dictionary of gibbs parameters. See below.

    Returns
    -------
    x_postmean : ndarray
       The deconvolued data (the posterior mean)

    chains : dict
       The keys 'noise' and prior contains the chain list of noise and
       prior precision respectively

    Other parameters
    ----------------
    The key of user_params are

    threshold : float
       The stopping criterion: the norm of the difference between to
       successive approximated solution (empirical mean of object
       sample). 1e-4 by default.

    burnin : int
       The number of sample to ignore to start computation of the
       mean. 100 by default.

    min_iter : int
       The minimum number of iteration. 30 by default.

    max_iter : int
       The maximum number of iteration if `threshold` is not
       satisfied. 150 by default.

    callback : None
       A user provided function to which is passed, if the function
       exists, the current image sample. This function can be used to
       store the sample, or compute other moments than the mean.

    References
    ----------
    .. [1] François Orieux, Jean-François Giovannelli, and Thomas
           Rodet, "Bayesian estimation of regularization and point
           spread function parameters for Wiener-Hunt deconvolution",
           J. Opt. Soc. Am. A 27, 1593-1607 (2010)

    http://www.opticsinfobase.org/josaa/abstract.cfm?URI=josaa-27-7-1593

    See Acknowledgements section in the package ``README.rst`` to know
    how to add a citation.
    """
    params = {'threshold': 1e-4, 'max_iter': 200,
              'min_iter': 30, 'burnin': 15, 'callback': None}
    params.update(user_params)

    if not reg:
        reg, _ = uft.laplacian(data.ndim, data.shape)
    if reg.dtype != np.complex:
        reg = uft.ir2tf(reg, data.shape)

    if imp_resp.shape != reg.shape:
        trans_func = uft.ir2tf(imp_resp, data.shape)
    else:
        trans_func = imp_resp

    # The mean of the object
    x_postmean = np.zeros(trans_func.shape)
    # The previous computed mean in the iterative loop
    prev_x_postmean = np.zeros(trans_func.shape)

    # Difference between two successive mean
    delta = np.NAN

    # Initial state of the chain
    gn_chain, gx_chain = [1], [1]

    # Parameter of the hyperparameter law. The following value
    # correspond to Jeffery's prior for the hyper parameter. See
    # reference.
    alpha_n, beta_n_bar = (0, 0)
    alpha_x, beta_x_bar = (0, 0)

    # The correlation of the object in Fourier space (if size is big,
    # this can reduce computation time in the loop)
    areg2 = np.abs(reg)**2
    atf2 = np.abs(trans_func)**2

    data_size = data.size
    data = uft.urfft2(data)

    # Gibbs sampling
    for iteration in range(params['max_iter']):
        # Sample of Eq. 27 p(circX^k | gn^k-1, gx^k-1, y).

        # weighing (correlation in direct space)
        precision = gn_chain[-1] * atf2 + gx_chain[-1] * areg2  # Eq. 29
        excursion = uft.crandn(data.shape) / np.sqrt(precision)

        # mean Eq. 30 (RLS for fixed gn, gamma0 and gamma1 ...)
        wiener_filter = gn_chain[-1] * np.conj(trans_func) / precision
        x_mean = wiener_filter * data

        # sample of X in Fourier space
        x_sample = x_mean + excursion
        if params['callback']:
            params['callback'](x_sample)

        # sample of Eq. 31 p(gn | x^k, gx^k, y)
        likelihood = uft.image_quad_norm(data - x_sample * trans_func)
        gn_chain.append(npr.gamma(alpha_n + data_size / 2,
                                  1 / (beta_n_bar + likelihood / 2)))

        # sample of Eq. 31 p(gx | x^k, gn^k-1, y)
        smoothness = uft.image_quad_norm(x_sample * reg)
        gx_chain.append(npr.gamma(alpha_x + (data_size - 1) / 2,
                                  1 / (beta_x_bar + smoothness / 2)))

        # current empirical average
        if iteration > params['burnin']:
            x_postmean = prev_x_postmean + x_sample

        if iteration > (params['burnin'] + 1):
            norm = np.sum(np.abs(x_postmean)) / (iteration - params['burnin'])
            current = x_postmean / (iteration - params['burnin'])
            previous = prev_x_postmean / (iteration - params['burnin'] - 1)

            delta = np.sum(np.abs(current - previous)) / norm

        prev_x_postmean = x_postmean

        # stop of the algorithm
        if (iteration > params['min_iter']) and (delta < params['threshold']):
            break

    # Empirical average \approx POSTMEAN Eq. 44
    x_postmean = x_postmean / (iteration - params['burnin'])
    x_postmean = uft.uirfft2(x_postmean)

    return (x_postmean, {'noise': gn_chain, 'prior': gx_chain})


def mudeconv(data, bounds, f_trans_func, reg=None, user_params={}):
    """Unsupervised Wiener-Hunt deconvolution

    return the deconvolution with a wiener-hunt approach, where the
    hyperparameters are estimated (or automatically tuned from a
    practical point of view). The algorithm is a stochastic iterative
    process (Gibbs sampler).

    This work can be free software. If you use this work add a
    citation to the reference below.

    Parameters
    ----------
    data : ndarray
       The data


    reg : ndarray, optional
       The regularisation operator. The laplacian by
       default. Otherwise, the same constraints that for `imp_resp`
       apply

    user_params : dict
       dictionary of gibbs parameters. See below.

    Returns
    -------
    x_postmean : ndarray
       The deconvolued data (the posterior mean)

    chains : dict
       The keys 'noise' and prior contains the chain list of noise and
       prior precision respectively

    Other parameters
    ----------------
    The key of user_params are

    threshold : float
       The stopping criterion: the norm of the difference between to
       successive approximated solution (empirical mean of object
       sample). 1e-4 by default.

    burnin : int
       The number of sample to ignore to start computation of the
       mean. 100 by default.

    min_iter : int
       The minimum number of iteration. 30 by default.

    max_iter : int
       The maximum number of iteration if `threshold` is not
       satisfied. 150 by default.

    callback : None
       A user provided function to which is passed, if the function
       exists, the current image sample. This function can be used to
       store the sample, or compute other moments than the mean.

    References
    ----------
    .. [1] François Orieux, Jean-François Giovannelli, and Thomas
           Rodet, "Bayesian estimation of regularization and point
           spread function parameters for Wiener-Hunt deconvolution",
           J. Opt. Soc. Am. A 27, 1593-1607 (2010)

    http://www.opticsinfobase.org/josaa/abstract.cfm?URI=josaa-27-7-1593

    See Acknowledgements section in the package ``README.rst`` to know
    how to add a citation.
    """
    params = {'threshold': 1e-4, 'max_iter': 200,
              'min_iter': 30, 'burnin': 15, 'callback': None}
    params.update(user_params)
    print params

    if not reg:
        reg, _ = uft.laplacian(data.ndim, data.shape)
    if reg.dtype != np.complex:
        reg = uft.ir2tf(reg, data.shape)

    trans_func = f_trans_func(np.mean(bounds))

    # The mean of the object
    x_postmean = np.zeros(trans_func.shape)
    # The previous computed mean in the iterative loop
    prev_x_postmean = np.zeros(trans_func.shape)

    # Difference between two successive mean
    delta = np.NAN

    # Initial state of the chain
    gn_chain, gx_chain, w_chain = [1], [1], [np.mean(bounds)]

    # Parameter of the hyperparameter law. The following value
    # correspond to Jeffery's prior for the hyper parameter. See
    # reference.
    alpha_n, beta_n_bar = (0, 0)
    alpha_x, beta_x_bar = (0, 0)

    # The correlation of the object in Fourier space (if size is big,
    # this can reduce computation time in the loop)
    areg2 = np.abs(reg)**2
    atf2 = np.abs(trans_func)**2

    data_size = data.size
    data = uft.urfft2(data)

    # Gibbs sampling
    for iteration in range(params['max_iter']):
        # Sample of Eq. 27 p(circX^k | gn^k-1, gx^k-1, y).

        # weighing (correlation in direct space)
        precision = gn_chain[-1] * atf2 + gx_chain[-1] * areg2  # Eq. 29
        excursion = uft.crandn(data.shape) / np.sqrt(precision)

        # mean Eq. 30 (RLS for fixed gn, gamma0 and gamma1 ...)
        wiener_filter = gn_chain[-1] * np.conj(trans_func) / precision
        x_mean = wiener_filter * data

        # sample of X in Fourier space
        x_sample = x_mean + excursion
        if params['callback']:
            params['callback'](x_sample)

        # sample of Eq. 31 p(gn | x^k, gx^k, y)
        likelihood = uft.image_quad_norm(data - x_sample * trans_func)
        gn_chain.append(npr.gamma(alpha_n + data_size / 2,
                                  1 / (beta_n_bar + likelihood / 2)))

        # sample of Eq. 31 p(gx | x^k, gn^k-1, y)
        smoothness = uft.image_quad_norm(x_sample * reg)
        gx_chain.append(npr.gamma(alpha_x + (data_size - 1) / 2,
                                  1 / (beta_x_bar + smoothness / 2)))

        # sample of Eq. 39 p(w | x^k, gn^k-1, y)
        w_proposition = npr.uniform(bounds[0], bounds[1])
        trans_func_prop = f_trans_func(w_proposition)
        likelihood_prop = uft.image_quad_norm(data - trans_func_prop * x_sample)
        criterion = gn_chain[-1] * (likelihood - likelihood_prop) / 2
        if np.log(npr.uniform()) < criterion:
            likelihood = likelihood_prop
            trans_func = trans_func_prop
            atf2 = np.abs(trans_func)**2
            w_chain.append(w_proposition)
        else:
            w_chain.append(w_chain[-1])

        # current empirical average
        if iteration > params['burnin']:
            x_postmean = prev_x_postmean + x_sample

        if iteration > (params['burnin'] + 1):
            norm = np.sum(np.abs(x_postmean)) / (iteration - params['burnin'])
            current = x_postmean / (iteration - params['burnin'])
            previous = prev_x_postmean / (iteration - params['burnin'] - 1)

            delta = np.sum(np.abs(current - previous)) / norm

        prev_x_postmean = x_postmean

        # stop of the algorithm
        if (iteration > params['min_iter']) and (delta < params['threshold']):
            break

    # Empirical average \approx POSTMEAN Eq. 44
    x_postmean = x_postmean / (iteration - params['burnin'])
    x_postmean = uft.uirfft2(x_postmean)

    return (x_postmean, {'noise': gn_chain, 'prior': gx_chain, 'instru': w_chain})
