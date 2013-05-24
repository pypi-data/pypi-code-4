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

  def __init__(self, batch_size, seed, regularization, grad_norm):
    """Initializes and loads the data
   
    seed
      An randomization seed (machine is initialized with it).

    regularization
      A regularization parameter to be passed to the MLP.

    grad_norm
      The norm of the projected gradient. Training with LBFGS-B will stop when the surface respects this degree of "flatness".
    """
    bob.trainer.overload.MLPBaseTrainer.__init__(self, batch_size)
    self.seed = seed
    self.regularization = regularization
    self.grad_norm = grad_norm

    self.activations = { bob.machine.Activation.LINEAR: lambda x: x,
       bob.machine.Activation.TANH: lambda x: numpy.tanh(x),
       bob.machine.Activation.LOG: lambda x: 1./(1.+math.exp(-x)),
       bob.machine.Activation.SIGMOID: lambda x: 1./(1.+math.exp(-x)) }
    self.activations_prime = { bob.machine.Activation.LINEAR: lambda x: 1.,
       bob.machine.Activation.TANH: lambda x: 1.-x*x,
       bob.machine.Activation.LOG: lambda x: x*(1.-x),
       bob.machine.Activation.SIGMOID: lambda x: x*(1.-x) }

  def initialize(self, machine):
    """Initializes the trainer for a specific machine"""
    bob.trainer.overload.MLPBaseTrainer.initialize(self, machine)

  def output_delta(self, output, y):
    """Returns the expected delta on the output layer (i.e. the derivate of the
    cost w.r.t. the activations on the last layer) if one uses the MSE cost as
    declared above."""

    # If you would like to ues the "Logistic Maximum Likelihood"-based cost,
    # replace the calculation of the return value by the following commented
    # out line. Please read the Notes section on ``J()`` above.

    # Note: This is the "naive" implementation of the output delta. In these
    #       settings we calculate delta here and then multiply that by the
    #       activation_prime() (which is (output * (1 - output)!) on the
    #       backward() implementation. Technically, this should cancel out.
    #       Nevertheless, if you find problems concerning this division on your
    #       training, I recommend you simplify the problem by removing the term
    #       (output * (1 - output)) here and slightly modifying backward() on
    #       the evaluation of ``self.delta2`` to take that into account,
    #       replacing the line that says:
    #
    #       self.delta2 = self.b2 * activation_prime(self.z2)
    #
    #       by:
    #
    #       self.delta2 = self.b2

    # ML logistic cost delta
    #return ((output - y) / (output * (1 - output))) / y.shape[1]

    # Use this for the MSE cost **or** ML logistic cost with the simplification
    # noted above
    return (output - y) / y.shape[0]

  def J(self, machine, X, y): 
    """Calculates the cost J, with regularization
    
    This version uses the Mean Square Error (MSE) as the cost with
    regularization:

      J_MSE(weights) = 0.5 * mean( (MLP(X)-y)^2 ) + ...
                          ... + (0.5 * lambda / N) * (sum(w1**2) + sum(w2**2))
    
    Keyword attributes:

    machine
      The MLP machine

    X
      The input vector containing examples organized in columns. The input
      matrix does **not** contain the bias term.

    y
      The expected output for the last layer of the network. This is a simple 2D
      numpy.ndarray containing 1 column vector for each input example in the
      original input vector X. Each column vector represents one output.

    Returns the ML (logistic regression) cost with regularization.
    """

    # If you would like to use the "Logistic Maximum Likelihood"-based cost,
    # replace the calculation of 'term1' by the following commented-out lines.
    #   
    # Note 1: Remember to change the definition of ``output_delta()`` below
    # Note 2: Remember to set activation function at ``__init__``, to the
    #         logistic function
    # Note 3: Notice that the "log" operation may underflow quite easily when a
    #         large number of examples (such as in M-NIST) are into play. If
    #         that happens, the cost may be set to +Inf and the minimization
    #         will stop abruptly. Using the MSE is a way to overcome this.

    # ML logistic cost term
    #h = self.forward(X)
    #logh = numpy.nan_to_num(numpy.log(h))
    #log1h = numpy.nan_to_num(numpy.log(1-h))
    #term1 = -(y*logh + ((1-y)*log1h)).sum() / y.shape[1]

    # MSE term
    term1 = 0.5 * numpy.sum( (machine.forward(X)-y)**2 ) / y.shape[0]
  
    # Regularization term
    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    term2 = (0.5 * self.regularization * (numpy.sum(w1**2) + numpy.sum(w2**2)) / y.shape[0])

    return term1 + term2

  def JandTheta(self, theta, machine, X, y): 
    """Calculates the vectorized cost *J*, by unrolling the theta vectors into the
    network weights.
    
    This version uses the Mean Square Error (MSE) as the cost with
    regularization:

      J_MSE(weights) = 0.5 * mean( (MLP(X)-y)^2 ) + ...
                          ... + (0.5 * lambda / N) * (sum(w1**2) + sum(w2**2))
    
    Keyword attributes:

    theta
      TODO

    machine
      The MLP machine

    X
      The input vector containing examples organized in columns. The input
      matrix does **not** contain the bias term.

    y
      The expected output for the last layer of the network. This is a simple 2D
      numpy.ndarray containing 1 column vector for each input example in the
      original input vector X. Each column vector represents one output.

    Returns the ML (logistic regression) cost with regularization.
    """

    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    w1_ = theta[:w1.size].reshape(w1.shape)
    w2_ = theta[w1.size:].reshape(w2.shape)
    machine.biases = [w1_[0,:], w2_[0,:]]
    machine.weights = [w1_[1:,:], w2_[1:,:]]

    return self.J(machine, X, y)

  def forward(self, machine, X):
    """Executes the forward step of a 2-layer neural network.

    Remember that:

    1. z = w^T . X

    and

    2. Output: a = g(z), with g being the logistic function

    Keyword attributes:

    X
      The input vector containing examples organized in columns. The input
      matrix does **not** contain the bias term.

    Returns the outputs of the network for each row in X. Accumulates hidden
    layer outputs and activations (for backward step). At the end of this
    procedure:
    
    a0
      Input, including the bias term for the hidden layer. 1 example per
      column. Bias = first row.

    z1
      Activations for every input X on hidden layer. z1 = w1^T * a0
    
    a1
      Output of the hidden layer, including the bias term for the output layer.
      1 example per column. Bias = first row. a1 = [1, act(z1)]

    z2
      Activations for the output layer. z2 = w2^T * a1.

    a2
      Outputs for the output layer. a2 = act(z2)

    Tip: You must first calculate the output of the first layer and then use
    that output to calculate the output of the second layer. It is not possible
    to do that at the same time.
    """

    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))

    activation = self.activations[machine.activation]
    output_activation = self.activations[machine.output_activation]

    a0 = numpy.hstack([numpy.ones(X.shape[0], dtype=float).reshape(X.shape[0],1), X])
    z1 = numpy.dot(w1.T, a0.T)
    a1 = activation(z1).T
    a1 = numpy.hstack([numpy.ones(a1.shape[0], dtype=float).reshape(a1.shape[0],1), a1])
    z2 = numpy.dot(w2.T, a1.T)
    a2 = output_activation(z2).T

    return (a0, a1, a2)



  def backward(self, machine, y, a0, a1, a2):
    """Executes the backward step for training.

    In this phase, we calculate the error on the output layer and then use
    back-propagation to estimate the error on the hidden layer. We then use
    this estimated error to calculate the differences between what the layer
    output and the expected value.

    Keyword attributes:

    y
      The expected output for the last layer of the network. This is a simple 1D
      numpy.ndarray containing 1 value for each input example in the original
      input vector X.

    a2
      Outputs for the output layer. a2 = act(z2)

    Sets the internal values for various variables:

    delta2
      Delta (derivative of J w.r.t. the activation on the last layer) for the
      output neurons:
      self.delta2_1 = (a2_1 - y) / (a2_1 * (1-a2_1)) / y.shape[1]
      N.B.: This is only valid if J is the ML logistic cost

    b2
      That is the back-propagated activation values, passing the delta values
      through the derivative of the activation function, w.r.t.  the previously
      calculated activation value: self.b2 = self.delta2 * activation'(z2) = 
      self.delta2 * (1 - a2**2) [if the activation function is tanh].

      N.B.: This is not a matrix multiplication, but an element by element
      multiplication as delta2 and a2 are single column vectors.

    delta1
      Delta (error) for the hidden layer. This calculated back-propagating the
      b's from the output layer back the neuron. In this specific case:
      self.delta1 = w2 * self.b2

      N.B.: This is a matrix multiplication

    b1
      Back-propagated activation values for hidden neurons. The analogy is the
      same: self.b1 = self.delta1 * activation'(z1) = self.delta1 * (1 - a1**2)

      N.B.: This is not a matrix multiplication, but an element by element
      multiplication as delta1 and a1 are single column vectors.

    d1, d2

      The updates for each synapse are simply the multiplication of the a's and
      b's on each end. One important remark to get this computation right: one
      must generate a weight change matrix that is of the same size as the
      weight matrix. If that is not the case, something is wrong on the logic

      self.dL = self.a(L-1) * self.b(L).T / number-of-examples

      N.B.: This **is** a matrix multiplication, despite a and b are vectors.
    """

    # For the next part of this exercise, you will complete the calculation of
    # the deltas and the weight updates (d). Before you start filling this,
    # make sure you scan the code for forward() so that you understand which
    # variables are already preset to you.

    # Evaluate deltas, b's and d's. In doubt, look at the comments above
    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    self.delta2 = self.output_delta(a2, y)
    output_activation_prime = self.activations_prime[machine.output_activation]
    activation_prime = self.activations_prime[machine.activation]
    self.b2 = self.delta2 * output_activation_prime(a2)
    self.delta1 = numpy.dot(w2[1:], self.b2.T).T
    self.b1 = self.delta1 * activation_prime(a1[:,1:])
    d2 = numpy.dot(a1.T, self.b2) / y.shape[0]
    d2 += (self.regularization / y.shape[0]) * w2
    d1 = numpy.dot(a0.T, self.b1) / y.shape[0]
    d1 += (self.regularization / y.shape[0]) * w1

    return (d1, d2)


  def dJ(self, theta, machine, X, y):
    """
    Calculates the vectorized partial derivative of the cost *J* w.r.t. to
    **all** :math:`\theta`'s. Use the training dataset.
    """
    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    w1_ = theta[:w1.size].reshape(w1.shape)
    w2_ = theta[w1.size:].reshape(w2.shape)
    machine.biases = [w1_[0,:], w2_[0,:]]
    machine.weights = [w1_[1:,:], w2_[1:,:]]

    #a0, a1, a2 = self.forward(machine, X)
    #d1, d2 = self.backward(machine, y, a0, a1, a2)

    self.forward_step(machine, X)
    self.backward_step(machine, y)


    ### print a0[:,1:] - X # OK
    ### print a1[:,1:] - self.output[0] # OK
    ### print a2 - self.output[1] # OK

    delta2 = self.error[1] / X.shape[0]
    delta1 = self.error[0]
    ### print self.delta2 - delta2 # OK
    ### print self.delta1 - delta1 # OK

    activation_prime = self.activations_prime[machine.activation]
    b2 = delta2 * activation_prime(self.output[1])
    b1 = self.error[0] * activation_prime(self.output[0])
    ### print self.b2 - b2 # OK
    ### print self.b1 - b1 # OK

    arg_a1 = numpy.vstack((numpy.ones(self.output[0].shape[0]), self.output[0].T))
    d2_ = numpy.dot(arg_a1, b2) / y.shape[0]
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    d2_ += (self.regularization / y.shape[0]) * w2
    ### print d2 - d2_ # OK
    arg_a0 = numpy.vstack((numpy.ones(X.shape[0]), X.T))
    d1_ = numpy.dot(arg_a0, b1) / y.shape[0]
    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    d1_ += (self.regularization / y.shape[0]) * w1
    #print d1 - d1_ # OK
    return numpy.hstack([d1_.flatten(), d2_.flatten()])

  def CER(self, machine, X, y):
    """Calculates the Classification Error Rate, a function of the weights of
    the network.

      CER = count ( round(MLP(X)) != y ) / X.shape[1]
    """

    est_cls = machine.forward(X).argmax(axis=1)
    cls = y.argmax(axis=1)

    return sum( cls != est_cls ) / float(X.shape[0])

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

    # TODO: check dimensionality of the machine 
    # TODO: check that the machine only has 1 hidden layer
    # TODO: check that the machine has a tanh activation function

    print 'Settings:'
    print '  * cost (J) = %g' % (self.J(machine, X, y),)
    cer = self.CER(machine, X, y)
    print('  * CER      = %g%% (%d sample(s))' % (100*cer, X.shape[0]*cer))
    print 'Training using scipy.optimize.fmin_l_bfgs_b()...'

    # theta0 is w1 and w2, flattened
    w1 = numpy.vstack((machine.biases[0], machine.weights[0]))
    w2 = numpy.vstack((machine.biases[1], machine.weights[1]))
    theta0 = numpy.hstack([w1.flatten(), w2.flatten()])

    # Fill in the right parameters so that the minimization can take place
    theta, cost, d = scipy.optimize.fmin_l_bfgs_b(
        self.JandTheta,
        theta0,
        self.dJ,
        (machine, X, y),
        pgtol=self.grad_norm,
        iprint=0,
        disp=2,
        )

    if d['warnflag'] == 0:

      print("** LBFGS converged successfuly **")
      print 'Final settings:'
      print '  * cost (J) = %g' % (cost,)
      #print '  * |cost\'(J)| = %s' % numpy.linalg.norm(d['grad'])
      cer = self.CER(machine, X, y)
      print('  * CER      = %g%% (%d sample(s))' % (100*cer, X.shape[0]*cer))

    else:
      print("LBFGS did **not** converged:")
      if d['warnflag'] == 1:
        print("  Too many function evaluations")
      elif d['warnflag'] == 2:
        print("  %s" % d['task'])

  def train_return(self, n_hidden, X, y):
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

    Returns a trained machine.
    """

    # prepare the machine
    
    # Initialize the seed like you did on the previous exercise
    rng = bob.core.random.mt19937(self.seed)

    n_inputs = X.shape[1]
    n_outputs = y.shape[1]
    shape = (n_inputs, n_hidden, n_outputs)
    machine = bob.machine.MLP(shape)
    machine.activation = bob.machine.Activation.TANH
    machine.randomize(rng)
    self.initialize(machine)
    self.train(machine, X, y)

    return machine




