#!/usr/bin/env python
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sat May 11 20:11:39 CEST 2013
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

import os
import sys
import argparse
import bob
import time

import xbob.db.mnist
import xbob.mlp.lbfgs
from .. import *

__epilog__ = """\
  To run the training process with default parameters, type:

    $ %(prog)s

  Use --help to see other options.
""" % {'prog': os.path.basename(sys.argv[0])}

def parse_args(command_line_parameters):
  """Defines and parses the command line arguments"""

  parser = argparse.ArgumentParser(description=__doc__, epilog=__epilog__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--seed', type=int, default=0,
      metavar='SEED (INT)', help="Random (initialization) seed (defaults to %(default)s)")

  parser.add_argument('-I', '--n-evaluations', default=50, type=int,
      metavar='INT', help="Maximum number of function evaluations (defaults to %(default)s)")

  parser.add_argument('-H', '--hidden', type=int, default=10,
      metavar='INT', help="Number of hidden units (defaults to %(default)s)")

  parser.add_argument('-n', '--projected-gradient-norm', type=float,
      default=1e-6, metavar='FLOAT', help='The norm of the projected gradient.  Training with LBFGS-B will stop when the surface respects this degree of "flatness" (defaults to %(default)s)')

  parser.add_argument('-d', '--mnist-data-dir', type=str,
      default=None, metavar='DATA_DIR', help="Path to the directory that contains the MNIST data (defaults to %(default)s)")

  parser.add_argument('-m', '--machine-file', default='mlp_lbfgs.hdf5',
      metavar='MACHINE', help="Path to the filename where to store the trained machine (defaults to %(default)s)")

  return parser.parse_args(command_line_parameters)

def lbfgs(args):
  """Executes the L-BFGS training"""

  ##### START of program
  print("M-NIST Digit Classification using a 2-layer MLP with tanh activation trained using an L-BFGS optimizer")
  print("Number of inputs               : %d" % (28*28,))
  print("Number of hidden units         : %d" % (args.hidden,))
  print("Number of outputs              : 10")
  if args.hidden == 0:
    n_free_params = (28*28+1)*10
  else:
    n_free_params = (28*28+1)*args.hidden+(args.hidden+1)*10
  print("Total number of free parameters: %d" % n_free_params)

  # Instantiate the MNIST database
  db = xbob.db.mnist.Database(args.mnist_data_dir)

  # Loads trainning set
  X_train, y_train, X_mean = utils.load_training_mean(db)
  y_train *= 0.8 # Restrict the outputs in [-0.8,0.8] for linearity purposes

  # Prepares MLP machine
  if args.hidden == 0:
    machine = bob.machine.MLP((28*28, 10))
  else:
    machine = bob.machine.MLP((28*28, args.hidden, 10))
  rng = bob.core.random.mt19937(args.seed)
  machine.randomize(rng)

  # Prepares MLP L-BFGS trainer
  trainer = xbob.mlp.lbfgs.Trainer(args.projected_gradient_norm, args.n_evaluations, X_train.shape[0])
  trainer.initialize(machine)
  # Launch training
  start = time.time()
  trainer.train(machine, X_train, y_train)
  total = time.time() - start
  sys.stdout.write("** Training is over, took %.2f minute(s)\n" % (total/60.))
  sys.stdout.flush()

  # Saves the machine
  utils.save_machine(X_mean, machine, args.machine_file)

  # Loads test set
  X_test, y_test = utils.load_test(db, X_mean)

  # Evaluates the performance of the machine on the test set
  utils.evaluate_machine(machine, X_test, y_test)

  return 0

def main(command_line_parameters = sys.argv):
  """Executes the main function"""
  args = parse_args(command_line_parameters[1:])
  return lbfgs(args)

if __name__ == "__main__":
  main()

