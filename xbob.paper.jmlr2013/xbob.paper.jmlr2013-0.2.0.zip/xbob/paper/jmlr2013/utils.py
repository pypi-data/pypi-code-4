#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @date: Fri May 10 19:45:16 CEST 2013
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

def __normalize_data__(X, labels):
  """Normalizes the data"""
  # creates a matrix for the MLP output in which only the correct label
  # position is set with +1.
  y = -1*numpy.ones((len(labels), 10), dtype=float)
  y[range(len(labels)), labels] = 1.0
  # Normalizing input set
  X  = X.astype(float)
  X  = ((X / 255.)) # * 2. - 1.)
  return (X, y)

def load_training_mean(db):
  """Loads the training set, compute the mean (over all the samples)
  and returns the samples, theirs labels and the mean vector computed
  over the samples.

  db 
    An instance of the xbob.db.mnist database
  """
  
  print("Loading M-NIST training set...")
  X_train, labels = db.data(groups='train') 
  # Normalizes
  X_train, y_train = __normalize_data__(X_train, labels)
  # Computes the mean
  X_mean   = X_train.mean(axis=0)
  # Removes the mean
  X_train -= X_mean
  return (X_train, y_train, X_mean)

def load_test(db, X_mean):
  """Loads the test set and returns the samples and theirs labels.

  db 
    An instance of the xbob.db.mnist database
  """
  
  print("Loading M-NIST test set...")
  X_test, labels = db.data(groups='test') 
  # Normalizes
  X_test, y_test = __normalize_data__(X_test, labels)
  # Removes the mean
  X_test -= X_mean
  return (X_test, y_test)

def save_machine(X_mean, machine, filename):
  """Saves the machine and the mean vector into an hdf5 file"""
  f = bob.io.HDF5File(filename, 'w')
  f.set('X_mean', X_mean)
  machine.save(f)
  del f

def load_machine(filename):
  """Loads the machine and the mean vector from an hdf5 file"""
  f = bob.io.HDF5File(filename)
  X_mean = f.read('X_mean')
  machine = bob.machine.MLP(f)
  return (X_mean, machine)

def cer(machine, X, y): 
  """Calculates the Classification Error Rate, a function of the weights of
  the network.

    CER = count ( round(MLP(X)) != y ) / X.shape[0]
  """

  est_cls = machine.forward(X).argmax(axis=1)
  cls = y.argmax(axis=1)

  return sum( cls != est_cls ) / float(X.shape[0])

def evaluate_machine(machine, X, y, group='Test'):
  """Evaluates the performance of the machine on the given set"""
  # Evaluate performaces
  trainer = bob.trainer.MLPRPropTrainer(X.shape[0], bob.trainer.SquareError(machine.output_activation))
  trainer.initialize(machine)
  print("** %s set results (%d examples):" % (group, X.shape[0]))
  print("  * cost (J) = %f" % trainer.cost(machine, X, y))
  cer_value = cer(machine, X, y)
  print('  * CER      = %g%% (%d sample(s))' % (100*cer_value, X.shape[0]*cer_value))

def scores_pos_neg(machine, X, y): 
  """Returns the list of positive and negative scores using the maximum score
  to take a decision.
  """

  scores = machine.forward(X)
  est_cls = scores.argmax(axis=1)
  cls = y.argmax(axis=1)
  positives = scores.max(axis=1)[est_cls == cls]
  negatives = scores.max(axis=1)[est_cls != cls]
  return (negatives, positives)

def plot_roc(scores, legends, filename):
  """Plots an ROC"""
  import matplotlib
  if not hasattr(matplotlib, 'backends'): matplotlib.use('pdf')
  import matplotlib.pyplot as mpl
  from matplotlib import rc
  # activate latex text rendering
  rc('text', usetex=True)

  if len(scores) != len(legends):
    raise 'Number of score files and legend names differ!'

  # ROC 
  fig = mpl.figure()
  linestyles = ['-','-.','--',':','steps'] #['', '-', '--', ':']
  linewidths = [1,2]
  for i in range(len(scores)):
    # Evaluates the performance of the machine on the test set
    npoints = 100
    negatives, positives = scores[i]
    bob.measure.plot.roc(negatives, positives, npoints, 
      linestyle=linestyles[i % len(linestyles)], linewidth=linewidths[i % len(linewidths)],
      label=legends[i])
  mpl.axis([0,40,0,40])
  mpl.title("ROC Curve")
  mpl.xlabel(r'FRR (\%)')
  mpl.ylabel(r'FAR (\%)')
  mpl.grid(True, color=(0.3,0.3,0.3))
  mpl.legend()
  mpl.savefig(filename)
