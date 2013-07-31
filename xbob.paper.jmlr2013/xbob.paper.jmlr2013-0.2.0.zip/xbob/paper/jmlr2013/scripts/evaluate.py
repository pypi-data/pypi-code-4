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
import numpy
import bob
import time
import matplotlib.pyplot as mpl

import xbob.db.mnist
from .. import *

__epilog__ = """\
  To run the evaluation process of an MLP, type:

    $ %(prog)s

  Use --help to see other options.
""" % {'prog': os.path.basename(sys.argv[0])}

def parse_args(command_line_parameters):
  """Parses the command line arguments"""

  parser = argparse.ArgumentParser(description=__doc__, epilog=__epilog__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-d', '--mnist-data-dir', type=str, 
      default=None, metavar='DATA_DIR', help="Path to the directory that contains the MNIST data (defaults to %(default)s)")

  parser.add_argument('-m', '--machine-file', default='mlp_rprop.hdf5',
      metavar='MACHINE', help="Path to the filename where to load the trained machine (defaults to %(default)s)")

  parser.add_argument('-t', '--training', action='store_true', default=False,
      help="Evaluate on the training set as well (defaults to %(default)s)")

  return parser.parse_args(command_line_parameters)

def evaluate(args):
  """Executes the evaluation"""

  ##### START of program
  print("M-NIST Digit Classification using an MLP")
  print("Number of inputs               : %d" % (28*28,))
  print("Number of outputs              : 10")

  # Instantiate the MNIST database
  db = xbob.db.mnist.Database(args.mnist_data_dir)

  # Loads the machine
  X_mean, machine = utils.load_machine(args.machine_file)

  if args.training:
    # Loads test set
    X_train, y_train, _ = utils.load_training_mean(db)
    # Evaluates the performance of the machine on the test set
    utils.evaluate_machine(machine, X_train, y_train, group='Training')

  # Loads test set
  X_test, y_test = utils.load_test(db, X_mean)
  # Evaluates the performance of the machine on the test set
  utils.evaluate_machine(machine, X_test, y_test)

  (pos, neg) = utils.scores_pos_neg(machine, X_test, y_test)

  return 0

def main(command_line_parameters = sys.argv):
  """Executes the main function"""
  args = parse_args(command_line_parameters[1:])
  return evaluate(args)

if __name__ == "__main__":
  main()

