#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 09:27:59 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
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

import facereclib
import argparse

import os
import sys

this_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
config_dir = os.path.join(this_dir, 'configs')


ALGORITHMS = {
    'LDA-IR' : ['--preprocessing', 'b-lda-ir',             '--features', 'b-lda-ir',      '--tool', 'b-lda-ir',      '--sub-directory', 'LDA-IR'],
    'Graphs' : ['--preprocessing', 'b-tan-triggs',         '--features', 'b-gabor-graph', '--tool', 'b-gabor-graph', '--sub-directory', 'Graphs'],
    'LGBPHS' : ['--preprocessing', 'b-tan-triggs-for-lbp', '--features', 'b-lgbphs',      '--tool', 'b-lgbphs',      '--sub-directory', 'LGBPHS'],
    'ISV'    : ['--preprocessing', 'b-tan-triggs',         '--features', 'b-isv',         '--tool', 'b-isv',         '--sub-directory', 'ISV'],
}

DATABASES = {
    'GBU'    : [os.path.join(this_dir, 'bin/faceverify_gbu.py')],
    'BANCA'  : [os.path.join(this_dir, 'bin/faceverify.py'), '--database', 'banca', '--groups', 'dev', 'eval']
}

SCRIPTS = {
    'GBU'    : facereclib.script.faceverify_gbu,
    'BANCA'  : facereclib.script.faceverify,
}

def grid(algorithm, database):
  if database == 'GBU' or algorithm in ('ISV', 'LGBPHS'):
    return ['--grid', 'b-demanding']
  else:
    return ['--grid', 'b-simple']

def local():
  return ['--grid', 'b-lobal']


def command_line_arguments(command_line_parameters):
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-a', '--algorithms', choices = ALGORITHMS.keys(), default = ALGORITHMS.keys(), nargs = '+', help = "Select one (or more) algorithms that you want to execute.")
  parser.add_argument('-d', '--databases', choices = DATABASES.keys(), default = DATABASES.keys(), nargs = '+', help = "The databases on which the baseline algorithms are executed.")
  parser.add_argument('-t', '--temp-directory', required = True, help = "Directory for temporary files.")
  parser.add_argument('-r', '--result-directory', required = True, help = "Directory to store result files.")

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them.")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid (only tested at Idiap).")
  parser.add_argument('-l', '--local', action = 'store_true', help = "Execute the algorithms in parallel on the local machine.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add the default logging options
  facereclib.utils.add_logger_command_line_option(parser)

  args = parser.parse_args(command_line_parameters)

  facereclib.utils.set_verbosity_level(args.verbose)

  return args


def main(command_line_parameters = None):
  args = command_line_arguments(command_line_parameters)

  # Iterate over all desired databases
  for database in args.databases:

    # Iterate over all desired algorithms
    for algorithm in args.algorithms:

      # Get the FaceRecLib script that is used for the current database
      call = DATABASES[database][:]

      # generate the arguments to call the FaceRecLib scripts...
      # add the configuration of the algorithm
      call.extend(ALGORITHMS[algorithm])
      # add the directories
      call.extend(['--temp-directory', os.path.join(args.temp_directory, database), '--result-directory', os.path.join(args.result_directory, database)])
      # add execution parameters
      if args.grid or args.local:
        # Create directory for the SQL3 database that will contain the steps of the face recognition experiment
        grid_database_dir = os.path.join('GRID', database, algorithm)
        facereclib.utils.ensure_dir(grid_database_dir)
        call.extend(['--submit-db-file', os.path.join(grid_database_dir, 'submitted.sql3')])

        # Use grid configurations that are
        if args.grid:
          call.extend(grid(algorithm, database))
        if args.local:
          call.extend(local())

      # append any additional parameters that were given on the command line split by -- (e.g. -- --force)
      if args.parameters:
        call.extend(args.parameters[1:])

      # for LDA-IR and GBU we use the extended training set -- to be comparable with the original results of Lui et al
      if database == 'GBU':
        if algorithm == 'LDA-IR':
          call.extend(['--database', 'b-gbu-x8'])
        else:
          call.extend(['--database', 'b-gbu-x2'])

      # increase the verbosity, if wanted
      if args.verbose:
        call.append("-"+"v"*args.verbose)

      # write to command line, what we will actually execute
      print(' '.join(call))

      # and execute it (if desired)
      if not args.dry_run:
        SCRIPTS[database].main(call)



