#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the L-BFGS-based MLP trainer.
"""

import numpy
import unittest
import bob

from . import Trainer

class MLPLbfgsTest(unittest.TestCase):
  """Performs various tests on the L-BFGS MLP-based trainer."""

  def test01(self):
    seed = 0
    regularization = 0.
    projected_gradient_norm = 1e-6
    n_hidden = 3
    n_samples = 100
    numpy.random.seed(seed)
    # Linearly separable problem
    X_train1 = numpy.random.randn(n_samples, 5) + 2
    X_train2 = numpy.random.randn(n_samples, 5) - 2
    X_train = numpy.vstack((X_train1, X_train2))
    y_train1 = numpy.hstack((numpy.ones(n_samples),-numpy.ones(n_samples)))
    y_train2 = numpy.hstack((-numpy.ones(n_samples),numpy.ones(n_samples)))
    y_train = numpy.vstack((y_train1, y_train2)).T

    machine = bob.machine.MLP((X_train.shape[1], n_hidden, y_train.shape[1]))
    machine.randomize()
    trainer = Trainer(projected_gradient_norm)
    trainer.initialize(machine)
    trainer.train(machine, X_train, y_train)

    # Computes output (of the training set)
    output = machine.forward(X_train)
    # Checks that all labels are correct
    self.assertTrue( numpy.all( y_train * output > 0 ) )
