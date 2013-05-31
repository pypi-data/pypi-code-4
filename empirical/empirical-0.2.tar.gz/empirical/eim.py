__all__ = [
    "EI",
]

import logging
from math import sqrt

import numpy as np

from empirical.utils import NDArrayDict


log = logging.getLogger(__name__)


class EI:

    def __init__(self, f, nodes, weights, parameters):
        """Creates an EI object, without calculating any basis functions.

        Parameters
        ==========
        * f: The function to construct an EI for. This must be a callable
             object that takes an element from `quadrature_nodes` as the first
             argument, followed by the parameters.
        * parameters: The candidate set of parameters. This is a numpy array,
             with shape (M, d), where d is the dimension of the parameter
             space.
        """
        self.f = f
        self.nodes = nodes
        self.weights = weights
        self.parameters = parameters

        self.Q = np.mat(np.zeros((self.nodes.shape[0], 0)))
        self.basis_max_x = np.zeros((0, self.nodes.shape[1]),
                                    dtype=self.nodes.dtype)
        self.basis_params = []
        self.B = np.mat(np.zeros((0, 0)))
        self.M = 0
        self.last_correction = float('inf')

    def ensure_capacity(self, M):
        if self.Q.shape[1] < M:
            Q = np.mat(np.empty((self.nodes.shape[0], M)))
            Q[:, :self.M] = self.Q[:, :self.M]
            self.Q = Q
        if self.basis_max_x.size < M:
            t = np.empty((M, self.nodes.shape[1]),
                         dtype=self.basis_max_x.dtype)
            t[:self.M] = self.basis_max_x[:self.M]
            self.basis_max_x = t
        if self.B.shape[0] < M:
            B = np.mat(np.zeros((M, M)))
            B[:self.M, :self.M] = self.B[:self.M, :self.M]
            self.B = B

    def reduce_capacity(self):
        if self.Q.shape[1] != self.M:
            Q = np.mat(np.empty((self.nodes.shape[0], self.M)))
            Q[:, :self.M] = self.Q[:, :self.M]
            self.Q = Q
        if self.basis_max_x.size != self.M:
            t = np.empty((self.M, self.nodes.shape[1]),
                         dtype=self.basis_max_x.dtype)
            t[:] = self.basis_max_x[:self.M]
            self.basis_max_x = t
        if self.B.shape[0] != self.M:
            B = np.mat(np.zeros((self.M, self.M)))
            B[:, :] = self.B[:self.M, :self.M]
            self.B = B

    def _prepare_basis(self):
        if not hasattr(self, "evaluations"):
            log.debug("Evaluating function for all parameters at given nodes.")
            evals = NDArrayDict()
            for params in self.parameters:
                f = lambda x: self.f(x, *params)
                evals[params] = f(self.nodes).reshape(self.nodes.shape[0])
            self.evaluations = evals  # pylint: disable=W0201
        self.ensure_capacity(self.M + 1)

    def add_basis(self):
        self._prepare_basis()

        # Find the maximum interpolant:
        max_params = None
        max_value = float('-inf')
        for i in range(self.parameters.shape[0]):
            params = self.parameters[i]
            evals = self.evaluations[params]
            # If there are no bases yet, use zero:
            if self.M == 0:
                I = np.zeros(self.nodes.shape[0])
            else:
                I = np.reshape(self.Q[:, :self.M] *
                               self.get_coeff(lambda x: self.f(x, *params)),
                               self.nodes.shape[0])
            maximum = np.amax(np.abs(evals - I))
            if maximum > max_value:
                max_value = maximum
                max_params = params
        self.basis_params.append(max_params)
        log.debug("New basis parameters: %s", max_params)

        # Now the base function for this interpolant is:
        ksi = lambda x: self.f(x, *max_params)
        evals = self.evaluations[max_params]

        # And the last interpolant at the new maximum is:
        if self.M == 0:
            I = np.zeros((self.nodes.shape[0], 1))
        else:
            I = self.Q[:, :self.M] * self.get_coeff(ksi)

        diff = evals.reshape((self.nodes.shape[0], 1)) - I
        max_index = np.argmax(np.abs(diff))
        new_max_x = self.nodes[max_index]
        log.debug("New basis maximum at x: %s", new_max_x)
        self.basis_max_x[self.M] = new_max_x
        self.Q[:, self.M] = (np.reshape(diff, (self.nodes.shape[0], 1)) /
                             (ksi(new_max_x) - I[max_index]))

        for j in range(self.M):
            self.B[j, self.M] = 0
            self.B[self.M, j] = self.Q[max_index, j]
        self.B[self.M, self.M] = 1

        #log.debug("B matrix is now:\n%s", self.B[:, :])

        self.M += 1

        log.info("Added new basis function (#%s), maximum correction is %s",
                 self.M, max_value)
        self.last_correction = max_value
        # Return the value that the interpolation was corrected by:
        return max_value

    def get_coeff(self, f, M=None):
        if M is None:
            M = self.M

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        b = f(self.basis_max_x[:M])
        y = np.linalg.solve(self.B[:M, :M], b.flat)
        return y.reshape((M, 1))

    def solve(self, M=None, tolerance=1e-10, test_params=None):
        if M is None:
            while self.last_correction > tolerance:
                self.add_basis()
            if not test_params is None:
                for p in test_params:
                    while self.L2_norm(p) > tolerance:
                        self.add_basis()
        else:
            self.ensure_capacity(M)
            while M > 0:
                self.add_basis()
                M -= 1

    def __call__(self, *params, M=None):
        if M is None:  # pylint: disable=E0601
            M = self.M

        if M == 0:
            return 0

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        phi = self.get_coeff(lambda x: self.f(x, *params), M)
        evals = 0
        for i in range(M):
            evals += (phi[i, 0] * self.Q[:, i])
        return evals

    def L2_norm(self, *params, M=None):
        if M is None:  # pylint: disable=E0601
            M = self.M

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        f_values = self.f(self.nodes, *params).flatten()
        calc = self(*params, M=M).flatten()  # pylint: disable=E1103,E1123

        abs_vals = np.abs(np.square(f_values - calc))
        return sqrt(np.sum(np.multiply(self.weights.flat, abs_vals.flat)))
