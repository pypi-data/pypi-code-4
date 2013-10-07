#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <manuel.guenther@idiap.ch>
# Wed Sep 25 09:16:55 CEST 2013
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
import os


from .utils import logger, init_logger, collect_score_files, compute_performance, ALGORITHMS

def command_line_arguments(command_line_parameters):
  """Defines the command line parameters that are accepted."""

  import argparse
  # create parser
  parser = argparse.ArgumentParser(description='Perform uni-modal fusion of algorithms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # add parameters
  parser.add_argument('-m', '--modality', choices=('face', 'speaker'), default=['face', 'speaker'], nargs='+', help = 'Select the modality (face, speaker or both) that you want to evaluate.')
  parser.add_argument('-p', '--protocol', choices=('male', 'female'), default=['male', 'female'], nargs='+', help = 'Select the protocols (male, female or both) that should be evaluated.')
  parser.add_argument('-d', '--data-directory', required=True, help = 'The directory where the score files can be found.')
  parser.add_argument('-l', '--latex-directory', help = 'The directory where the resulting tables (in LaTeX format) should be written (if not given, no file will be written; works only if both protocols are evaluated).')

  parser.add_argument('-n', '--limit-algorithms', type=int, help = 'Limit the number of algorithms to the given number (mainly for debug purposes).')
  parser.add_argument('-v', '--verbose', action='count', default=0, help = 'Increase the verbosity level from ERROR (0) to WARNING (1), INFO (2) and DEBUG (3).')

  # evaluate command line arguments
  args = parser.parse_args(command_line_parameters)

  # set logging level
  init_logger(args.verbose)

  return args


def write_latex(latex_file, results, modality):
  """Writes the results for the given modality into a LaTeX-compatible format.
  In LaTeX, simply define the \Result macro and import the generated file."""

  # re-order the results
  data = [(results['male'][i][0], results['male'][i][1], results['female'][i][0], results['female'][i][1]) for i in range(len(results['male']))]
  count = len(data)

  # get the best results per column
  best = [min([data[t][i] for t in range(count)]) for i in range(4)]

  # write the results
  with open(latex_file, 'w') as f:
    # iterate over the n-best fused systems
    for t in range(count):
      # create abbreviation for system
      system = '%s-%d' % ({'speaker':'S', 'face':'F'}[modality], t+1)
      # write abbreviation and long name
      f.write('\\Result{%s} {%s} {'%(system, ALGORITHMS[system].replace('_','-')))

      # write EER and HTER for male and female
      for i in range(4):
        if data[t][i] == best[i]:
          f.write('\\bf ')
        f.write('%3.2f'%(data[t][i]*100.))
        if i < 3:
          f.write("} {")
        else:
          f.write("}\n")


def main(command_line_parameters = None):
  """Main function that is executed during the call of the script."""
  # get the command line arguments
  args = command_line_arguments(command_line_parameters)

  # iterate over the desired modalities
  for modality in args.modality:

    # collect results for all protocols of the current modality
    results = {}
    for protocol in args.protocol:
      # collect the score file names for the protocols
      files_dev = collect_score_files(args.data_directory, modality, protocol, 'dev', args.limit_algorithms)[0]
      files_eval = collect_score_files(args.data_directory, modality, protocol, 'eval', args.limit_algorithms)[0]

      # read the scores for the development set
      logger.info('Loading %d score files of the development set' % len(files_dev))
      scores_dev = [bob.measure.load.split_four_column(file_name) for file_name in files_dev]

      results[protocol] = []

      # iterate over all systems
      for i in range(len(scores_dev)):
        # compute the performance of the raw scores
        eer, hter = compute_performance(files_dev[i], files_eval[i])
        logger.info('Results for modality %s, protocol %s and system %d is: EER %f%%, HTER %f%%' % (modality, protocol, i+1, eer*100, hter*100))
        results[protocol].append((eer, hter))

    # check if LaTeX output is desired
    if args.latex_directory:
      # create LaTeX file name
      latex_file = os.path.join(args.latex_directory, 'single_%s.tex' % modality)
      logger.info('Writing LaTeX-compatible result file %s' % latex_file)
      bob.io.create_directories_save(os.path.dirname(latex_file))
      # write the results
      write_latex(latex_file, results, modality)
