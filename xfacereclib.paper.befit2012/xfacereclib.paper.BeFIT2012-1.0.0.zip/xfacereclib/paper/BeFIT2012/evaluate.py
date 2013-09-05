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

import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages

# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
# increase the default font size
matplotlib.rc('font', size=22)


import argparse
import os
import numpy
import math
import bob
import subprocess
import facereclib

from .execute import ALGORITHMS, DATABASES

def command_line_arguments(command_line_parameters):
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--result-directory', required = True, help = "Directory, where the results of the experiments are stored.")
  parser.add_argument('-a', '--algorithms', choices = ALGORITHMS.keys(), default = ALGORITHMS.keys(), nargs = '+', help = "Select one (or more) algorithms that you want to evaluate")
  parser.add_argument('-d', '--databases', choices = DATABASES.keys(), default = DATABASES.keys(), nargs = '+', help = "The databases on which the baseline algorithms are evaluated")

  parser.add_argument('-p', '--gbu-plot-file', default='GBU.pdf', help = "The file to contain the GBU plot.")

  parser.add_argument('--score-file', default="scores", help = argparse.SUPPRESS)
  parser.add_argument('--titles', action='store_false', help = argparse.SUPPRESS)

  # add the default logging options
  facereclib.utils.add_logger_command_line_option(parser)
  # parse command line
  args = parser.parse_args(command_line_parameters)
  # set vebosity level
  facereclib.utils.set_verbosity_level(args.verbose)

  return args


def parse_results(directory, filename, algorithms):
  """Iterates through the given directory and collects result files for the given algorithms with the given filename."""
  # check, for which algorithms there are some results
  available_algorithms = os.listdir(directory)
  # check, which of these should be evaluated
  desired_algorithms = set(algorithms).intersection(set(available_algorithms))

  # collect all result files
  results = {}
  for algorithm in desired_algorithms:
    algo_results = {}
    # use os.walk to get all files of the current's algorithm's directory
    for root, dirs, files in os.walk(os.path.join(directory, algorithm)):
      # check if the desired filename is in the diretory
      if filename in files:
        # get the protocol name
        protocol = os.path.basename(os.path.dirname(root))
        facereclib.utils.debug("Found result file %s" % os.path.join(root, filename))
        # remember the result file for the protocol
        algo_results[protocol] = os.path.join(root, filename)
    # add the result files for our algorithm
    results[algorithm] = algo_results

  # assert that we have results for all desired algorithms
  for algorithm in desired_algorithms:
    if algorithm not in results:
      facereclib.utils.error("Could not read the results for the %s algorithm from directory %s" % (algorithm, directory))

  return results


def main_gbu(args):
  """Collects the results of the GBU database and generates a plot."""

  facereclib.utils.info("Evaluating the GBU database")
  # collect all result files for the GBU experiments in the given directory
  result_files = parse_results(os.path.join(args.result_directory, 'GBU'), args.score_file + "-dev", args.algorithms)

  # check that result files could be read
  if not result_files:
    raise IOError("Cannot read the result files of the GBU database from %s" % os.path.join(args.result_directory, 'GBU'))

  # evaluate three protocols
  protocols = ('Good', 'Bad', 'Ugly')

  # compute default FAR steps, logarithmically from 0.0001 to 1
  far = numpy.ndarray((17,), dtype=numpy.float64)
  for i in range(-16,0):
    far[i+16] = math.pow(10., i * 0.25)
  far[16] = 1.

  # get the results
  facereclib.utils.debug("Computing results for %d algorithms" % len(result_files))
  results = {}
  for protocol in protocols:
    # collect FAR's and FRR's for the current protocol
    results[protocol] = {}
    for algorithm in sorted(result_files.keys()):
      # check if the result for the given protocol in the given algorithm exist
      if protocol in result_files[algorithm]:
        # read the result files
        neg, pos = bob.measure.load.split_four_column(result_files[algorithm][protocol])
        # check that both positive (client) and negative (impostor) scores exist
        if len(neg) and len(pos):
          # compute the FRR for the given score files at the given FAR values
          results[protocol][algorithm] = bob.measure.roc_for_far(neg, pos, far)

  # plot the results
  facereclib.utils.debug("Evaluating")
  # create a multi-page PDF
  pdf = PdfPages(args.gbu_plot_file)
  # get the color map
  cmap = mpl.cm.get_cmap(name='hsv')

  # iterate over the protocols
  for protocol in protocols:
    # create a separate figure in the
    figure = mpl.figure()

    # get enough colors from the color map
    colors = [cmap(i) for i in numpy.linspace(0, 1.0, len(results[protocol])+1)]
    color_map = {}
    for i in range(len(results[protocol])):
      color_map[results[protocol].keys()[i]] = colors[i]

    # plot FAR and FRR for each algorithm
    for algo in results[protocol]:
      res = results[protocol][algo]
      mpl.semilogx(100.0*res[0,:], 100.0*res[1,:], label=algo)
      # print the CAR at 0.1% FAR to command line
      print("Database GBU, Protocol %s, Algorithm %s, CAR: %3.1f%%"% (protocol, algo, (100. * res[1,4])))

    # finalize plot
    mpl.plot([0.1,0.1],[0,100], "--", color=(0.3,0.3,0.3))
    mpl.axis([far[0]*100,100,0,100])
    mpl.xticks((0.01, 0.1, 1, 10, 100), ('0.01', '0.1', '1', '10', '100'))
    mpl.xlabel('FAR (\%)')
    mpl.ylabel('CAR (\%)')
    mpl.grid(True, color=(0.6,0.6,0.6))
    mpl.legend(loc=4 if protocol in ('Good','Bad') else 2)
    if args.titles:
      mpl.title(protocol)

    # close pdf page
    pdf.savefig(figure)

  # close figure
  pdf.close()
  facereclib.utils.info("Wrote plot %s" % args.gbu_plot_file)


def main_banca(args):
  """Collects the results of the BANCA database and reports them on command line."""
  facereclib.utils.info("Evaluating the BANCA database")
  # collect results for development and evaluation set of the BANCA database
  result_files_dev = parse_results(os.path.join(args.result_directory, 'BANCA'), args.score_file + "-dev", args.algorithms)
  result_files_eval = parse_results(os.path.join(args.result_directory, 'BANCA'), args.score_file + "-eval", args.algorithms)

  # check if result files could be found
  if not result_files_dev or not result_files_eval:
    raise IOError("Cannot read the result files of the BANCA database from %s" % os.path.join(args.result_directory, 'BANCA'))

  # read and evaluate the results
  results = {}
  for algorithm in sorted(result_files_dev.keys()):
    # for BANCA, there is only the "P" protocol evaluated
    if 'P' in result_files_dev[algorithm] and 'P' in result_files_eval[algorithm]:
      # get the positive (client) and negative (impostor) scores for both sets
      neg_d, pos_d = bob.measure.load.split_four_column(result_files_dev[algorithm]['P'])
      neg_e, pos_e = bob.measure.load.split_four_column(result_files_eval[algorithm]['P'])
      # check that all files have successfully been read
      if len(neg_d) and len(pos_d) and len(neg_e) and len(pos_e):
        # compute the threshold based on the EER of the development set
        threshold = bob.measure.eer_threshold(neg_d, pos_d)
        # compute the EER on the development set using this threshold
        far, frr = bob.measure.farfrr(neg_d, pos_d, threshold)
        eer_d = (far + frr) / 2.

        # compute the HTER of the evaluation set using the same threshold
        far, frr = bob.measure.farfrr(neg_e, pos_e, threshold)
        hter_e = (far + frr) / 2.
        # report the results on command line
        print ("Database BANCA, Algorithm %s, EER: %3.1f%%, HTER: %3.1f%%" % (algorithm, (100. * eer_d), 100. * hter_e))


def main(command_line_parameters = None):
  """Main function; Checks command line arguments and calls the according functions to evaluate GBU and BANCA experiments."""
  args = command_line_arguments(command_line_parameters)

  if "GBU" in args.databases:
    main_gbu(args)

  if "BANCA" in args.databases:
    main_banca(args)


if __name__ == '__main__':
  main()

