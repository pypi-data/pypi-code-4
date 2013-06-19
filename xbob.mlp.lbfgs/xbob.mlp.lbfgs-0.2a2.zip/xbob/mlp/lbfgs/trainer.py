#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @date: Wed May 8 19:42:39 CEST 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import bob
import numpy
import scipy.optimize


class Trainer(bob.trainer.overload.MLPBaseTrainer):
  """Trains an MLP machine using LBFGS-B.
  This class is an adaptation from Andre Anjos' implementation for the 
  lab 3 of the 2013 EPFL EDEE-612 `Fundamentals in Statistical Pattern Recognition` 
  course (http://www.idiap.ch/~marcel/professional/EPFL_2013.html)"""

  def __init__(self, grad_norm, max_eval=0):
    """Initializes and loads the data
   
    grad_norm
      The norm of the projected gradient. Training with LBFGS-B will stop when the surface respects this degree of "flatness".

    max_eval
      The maximum number of evaluation of the cost function before terminating the optimization.
      This is ignored if set to 0.
    """
    bob.trainer.overload.MLPBaseTrainer.__init__(self, 1, bob.trainer.SquareError(bob.machine.HyperbolicTangentActivation()))
    self.grad_norm = grad_norm
    self.max_eval = max_eval

  def initialize(self, machine):
    """Initializes the trainer for a specific machine"""
    bob.trainer.overload.MLPBaseTrainer.initialize(self, machine)

  def j_cost(self, machine, X, y): 
    """Calculates the cost J
    
    This version uses the Mean Square Error (MSE) as the cost:

      J_MSE(weights) = 0.5 * mean( (MLP(X)-y)^2 )
    
    machine
      The MLP machine

    X
      The input vector containing examples organized in columns. The input
      matrix does **not** contain the bias term.

    y
      The expected output for the last layer of the network. This is a simple 2D
      numpy.ndarray containing 1 column vector for each input example in the
      original input vector X. Each column vector represents one output.

    Returns the MSE cost.
    """
    return 0.5 * numpy.sum( (machine.forward(X)-y)**2 ) / y.shape[0]

  def update_machine_with_theta(self, theta, machine):
    """Unvectorizes the coefficients in the theta vector, and assigns them to
    the biases and the weights of the machine.

    theta
      Theta used by the L-BFGS optimizer

    machine
      The MLP machine
    """
    Nw = len(machine.weights) # Number of layers
    biases = []
    weights = []
    ind_c = 0
    for l in range(Nw):
      # Get the biases for this layer from theta
      size_biases = machine.biases[l].size
      b_ = theta[ind_c:ind_c+size_biases]
      biases.append(b_)
      ind_c += size_biases
      # Get the layers for this layer from theta
      size_weights = machine.weights[l].size
      w_ = theta[ind_c:ind_c+size_weights].reshape(machine.weights[l].shape)
      ind_c += size_weights
      weights.append(w_)
    machine.biases = biases
    machine.weights = weights

  def j_and_theta(self, theta, machine, X, y): 
    """Calculates the vectorized cost *J*, by unrolling the theta vectors into the
    network weights.
    
    This version uses the Mean Square Error (MSE) as the cost:

      J_MSE(weights) = 0.5 * mean( (MLP(X)-y)^2 )
    
    Keyword attributes:

    theta
      Theta used by the L-BFGS optimizer

    machine
      The MLP machine

    X
      The input vector containing examples organized in columns. The input
      matrix does **not** contain the bias term.

    y
      The expected output for the last layer of the network. This is a simple 2D
      numpy.ndarray containing 1 column vector for each input example in the
      original input vector X. Each column vector represents one output.

    Returns the MSE cost.
    """

    self.update_machine_with_theta(theta, machine)
    return self.j_cost(machine, X, y)

  def dj(self, theta, machine, X, y):
    """
    Calculates the vectorized partial derivative of the cost *J* w.r.t. to
    **all** :math:`\theta`'s. Use the training dataset.
    """
    self.update_machine_with_theta(theta, machine)

    self.forward_step(machine, X)
    self.backward_step(machine, y)
    self.cost_derivatives_step(machine, X)

    d = []
    Ne = len(self.deriv)
    for k in range(Ne):
      d.append(self.deriv_bias[k].flatten())
      d.append(self.deriv[k].flatten())
    return numpy.hstack(d)

  def train(self, machine, X, y):
    """
    Optimizes the machine parameters to fit the input data, using
    ``scipy.optimize.fmin_l_bfgs_b``.

    Keyword parameters:

    machine
      The MLP machine (with a single hidden layer) to train

    X
      The input data matrix. This must be a numpy.ndarray with 2 dimensions.
      Every column corresponds to one example of the data set, every row, one
      different feature. The input data vector X must not have the bias column
      added. It must be pre-normalized if necessary.

    y
      The expected output data matrix.
    """

    self.batch_size = X.shape[0]
    if (X.shape[0] != y.shape[0]):
      raise 'Number of samples in the training set and number of labels do not match!'

    print 'Settings:'
    print '  * cost (J) = %g' % (self.j_cost(machine, X, y),)
    print 'Training using scipy.optimize.fmin_l_bfgs_b()...'

    # theta0 is w1 and w2, flattened
    w_ = []
    for l in range(len(machine.weights)):
      w_.append(numpy.vstack((machine.biases[l], machine.weights[l])).flatten())
    theta0 = numpy.hstack(w_)

    # Fill in the right parameters so that the minimization can take place
    if self.max_eval != 0:
      theta, cost, d = scipy.optimize.fmin_l_bfgs_b(
        self.j_and_theta, theta0, self.dj, (machine, X, y),
        pgtol=self.grad_norm, iprint=0, disp=2, maxfun=self.max_eval)
    else:
      theta, cost, d = scipy.optimize.fmin_l_bfgs_b(
        self.j_and_theta, theta0, self.dj, (machine, X, y),
        pgtol=self.grad_norm, iprint=0, disp=2)

    if d['warnflag'] == 0:
      print("** LBFGS converged successfuly **")
      print 'Final settings:'
      print '  * cost (J) = %g' % (cost,)
    else:
      if d['warnflag'] == 1:
        print("** LBFGS: Maximum number of function evaluations reached **")
        print 'Final settings:'
        print '  * cost (J) = %g' % (cost,)
      elif d['warnflag'] == 2:
        print("LBFGS did **not** converged:")
        print("  %s" % d['task'])

