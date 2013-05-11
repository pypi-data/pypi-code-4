from __future__ import division

__copyright__ = "Copyright (C) 2012 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
import numpy.linalg as la

"""Legendre smoothness estimation."""




def make_mode_number_vector(lege_exp, ignored_modes):
    node_cnt = lege_exp.node_count

    mode_number_vector = np.zeros(node_cnt-ignored_modes, dtype=np.float64)
    for i, mid in enumerate(lege_exp.mode_identifiers):
        if i < ignored_modes:
            continue
        mode_number_vector[i-ignored_modes] = sum(mid)

    return mode_number_vector




def create_decay_baseline(lege_exp, ignored_modes):
    """Create a vector of modal coefficients that exhibit 'optimal'
    (:math:`k^{-N}`) decay.
    """

    mode_numbers = make_mode_number_vector(lege_exp, ignored_modes)
    zeros = mode_numbers == 0

    modal_coefficients = mode_numbers**(-lege_exp.order)
    modal_coefficients[zeros] = 1 # irrelevant, just keeps log from NaNing

    modal_coefficients /= la.norm(modal_coefficients)

    return modal_coefficients




def get_decay_fit_matrix(lege_exp, ignored_modes, weight_vector):
    node_cnt = lege_exp.node_count

    mode_number_vector = make_mode_number_vector(lege_exp, ignored_modes)

    a = np.zeros((node_cnt-ignored_modes, 2), dtype=np.float64)
    a[:,0] = weight_vector
    a[:,1] = weight_vector * np.log(mode_number_vector)

    if ignored_modes == 0:
        assert not np.isfinite(a[0,1])
        a[0,1] = 0

    return la.pinv(a)




def skyline_pessimize(modal_values):
    nelements, nmodes = modal_values.shape

    result = np.empty_like(modal_values)

    for iel in xrange(nelements):
        my_modes = modal_values[iel]
        cur_val = max(my_modes[-1], my_modes[-2])

        for imode in xrange(nmodes-1, -1, -1):
            if my_modes[imode] > cur_val:
                cur_val = my_modes[imode]

            result[iel, imode] = cur_val

    return result




def fit_modal_decay_from_modes(modal_values, lege_exp, ignored_modes=1):
    """See http://arxiv.org/abs/1102.3190 for details.

    :arg nodal_values: a numpy array of shape (num_elements, num_nodes)
    """

    weight_vector = np.ones(lege_exp.node_count - ignored_modes, dtype=np.float64)

    coeffs = modal_values
    coeffs_squared = skyline_pessimize(coeffs**2)

    fit_mat = get_decay_fit_matrix(lege_exp, ignored_modes,
            weight_vector)

    el_norm_squared = np.sum(coeffs_squared, axis=-1)
    scaled_baseline = (
            create_decay_baseline(lege_exp, ignored_modes)
            * el_norm_squared[:, np.newaxis])**2
    log_modal_coeffs = np.log(coeffs_squared[:, ignored_modes:] + scaled_baseline)/2

    assert fit_mat.shape[0] == 2 # exponent and log constant

    fit_values = np.dot(fit_mat, (weight_vector*log_modal_coeffs).T).T

    exponent = fit_values[:, 1]
    const = np.exp(fit_values[:, 0])

    if 0:
        import matplotlib.pyplot as pt
        pt.plot(log_modal_coeffs.flat, "o-")

        mode_nr = make_mode_number_vector(lege_exp, ignored_modes)
        fit = np.log(const[:, np.newaxis] * mode_nr**exponent[:, np.newaxis])

        pt.plot(fit.flat)

        #plot_expt = np.zeros_like(log_modal_coeffs)
        #plot_expt[:] = exponent[:, np.newaxis]
        #pt.plot(plot_expt.flat)

        pt.show()

    return exponent, const




def fit_modal_decay(nodal_values, lege_exp, ignored_modes=1):
    """See http://arxiv.org/abs/1102.3190 for details.

    :arg nodal_values: a numpy array of shape (num_elements, num_nodes)
    """

    coeffs = np.dot(lege_exp.inv_vdm, nodal_values.T).T
    return fit_modal_decay_from_modes(coeffs, lege_exp, ignored_modes)




def estimate_relative_expansion_residual(nodal_values, lege_exp, ignored_modes=1):
    """Implements the Mavriplis et al error estimator, by using the
    fit as an estimate of the entire modal decay and comparing this
    to the norm captured by the expansion.

    :arg nodal_values: a numpy array of shape (num_elements, num_nodes)
    """

    coeffs = np.dot(lege_exp.inv_vdm, nodal_values.T).T

    ignored_l2_parts = np.sum(coeffs[:, :ignored_modes]**2, axis=-1)
    captured_l2_parts = np.sum(coeffs[:, :ignored_modes]**2, axis=-1)
    l2_norms = ignored_l2_parts + captured_l2_parts

    exponent, const = fit_modal_decay_from_modes(coeffs, lege_exp, ignored_modes)

    residuals = const* (-lege_exp.order**(exponent+1)/(exponent+1))

    assert (residuals > 0).all()

    return residuals/l2_norms

