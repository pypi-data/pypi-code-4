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
import math
import os

from .utils import logger, init_logger, collect_score_files, fuse_scores, compute_performance


def parse_command_line(command_line_options):
  """Defines the command line parameters that are accepted."""

  import argparse
  parser = argparse.ArgumentParser(description='Perform bi-modal fusion of algorithms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-m', '--modality', choices=('face', 'speaker'), default=['face', 'speaker'], nargs='+', help = 'Select the modality (face, speaker or both) that you want to evaluate.')
  parser.add_argument('-p', '--protocol', choices=('male', 'female'), default=['male', 'female'], nargs='+', help = 'Select the protocols (male, female or both) that should be evaluated.')
  parser.add_argument('-d', '--data-directory', required=True, help = 'The directory where the score files can be found.')
  parser.add_argument('-o', '--fused-directory', default='fused/bimodal', help = 'The directory where the fused score files should be written to; if the files already exist, they are not re-created.')
  parser.add_argument('-f', '--force', action='store_true', help = 'Force the result files to be re-created even if they already exist.')
  parser.add_argument('-w', '--plot-file', default = 'bimodal.pdf', help = 'The pdf file where the graphics should be plotted into.')

  parser.add_argument('-n', '--limit-algorithms', type=int, help = 'Limit the number of algorithms that will be fused (mainly for debug purposes).')
  parser.add_argument('-v', '--verbose', action='count', default=0, help = 'Increase the verbosity level from ERROR (0) to WARNING (1), INFO (2) and DEBUG (3).')

  args = parser.parse_args(command_line_options)

  # set logging level
  init_logger(args.verbose)

  return args



def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  # get the command line options
  args = parse_command_line(command_line_options)

  # collect the best systems and their results per protocol
  best_systems = {}
  results = {}

  # iterate over the desired protocols
  for protocol in args.protocol:
    # collect the all development set score files that we need
    dev_score_files, eval_score_files = {}, {}
    for modality in args.modality:
      for group, score_files in {'dev' : dev_score_files, 'eval' : eval_score_files}.iteritems():
        files, names = collect_score_files(args.data_directory, modality, protocol, group)
        for i in range(len(files)):
          score_files[names[i]] = files[i]
    logger.info('Collected %d raw score files for protocol %s' % (len(dev_score_files), protocol))

    # read data
    logger.info('Reading score files of the development set')
    dev_scores = {system : bob.measure.load.split_four_column(dev_score_files[system]) for system in dev_score_files}

    # evaluate optimal score fusion...
    logger.info('Evaluating')
    number_of_algorithms = len(dev_scores) if args.limit_algorithms is None or args.limit_algorithms > len(dev_scores) else args.limit_algorithms
    best_systems[protocol] = []
    results[protocol] = []
    # iterate over the desired number of fused algorithms
    for i in range(number_of_algorithms):
      # get the file names of the fused score files
      dev_result_file = os.path.join(args.fused_directory, '%s_%s_best_%d.txt' % (protocol, 'dev', i+1))
      eval_result_file = os.path.join(args.fused_directory, '%s_%s_best_%d.txt' % (protocol, 'eval', i+1))
      best_systems_file = os.path.join(args.fused_directory, '%s_systems_%d.txt' % (protocol, i+1))

      # check if the fused score files already exist
      if os.path.exists(dev_result_file) and os.path.exists(eval_result_file) and os.path.exists(best_systems_file) and not args.force:
        # read the data from file instead of re-computing
        best_systems[protocol].append(open(best_systems_file).read().rstrip())
        logger.info('Skipping the creation of the existing files %s and %s, and take the former best result %s instead' % (dev_result_file, eval_result_file, best_systems[protocol][-1]))
      else:
        # search for the next system that should
        bob.io.create_directories_save(os.path.dirname(dev_result_file))
        # get the dev scores of the best systems so far
        if best_systems[protocol]:
          negatives = numpy.vstack([dev_scores[system][0] for system in best_systems[protocol]]).T
          positives = numpy.vstack([dev_scores[system][1] for system in best_systems[protocol]]).T
        else:
          negatives = None
          positives = None

        # iterate over all remaining systems
        best_eer = 1.
        best_additional_system = None
        best_machine = None
        for system in dev_scores:
          # test if we haven't added the system yet
          if system not in best_systems[protocol]:
            logger.debug('Temporarily adding system %s' % system)
            # get an extended set of scores using the best systems and the currently added one
            if negatives is not None and positives is not None:
              extended_negatives = numpy.append(negatives.copy(), numpy.reshape(dev_scores[system][0], (negatives.shape[0],1)), axis=1)
              extended_positives = numpy.append(positives.copy(), numpy.reshape(dev_scores[system][1], (positives.shape[0],1)), axis=1)
            else:
              extended_negatives = numpy.vstack([dev_scores[system][0]]).T
              extended_positives = numpy.vstack([dev_scores[system][1]]).T

            # train the fusion with the extended set of systems
            trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
            machine = trainer.train(extended_negatives, extended_positives.copy())

            # fuse client and impostor scores of the current set
            fused_negatives = machine(extended_negatives)[:,0]
            fused_positives = machine(extended_positives)[:,0]

            # compute the eer on the development set with the fused scores (should be around 0)
            threshold = bob.measure.eer_threshold(fused_negatives, fused_positives)
            # compute FAR and FRR at this threshold
            far, frr = bob.measure.farfrr(fused_negatives, fused_positives, threshold)
            # compute the equal error rate on the development set
            eer = (far + frr) / 2.
            logger.debug('Result of additional system %s is %f%% EER' % (system, eer*100.))

            # check if this system is better than the one before
            if eer < best_eer:
              # system is better -> this is the best system now
              best_eer = eer
              best_additional_system = system
              best_machine = machine

        # write the best additional system
        logger.info('Found best additional system to be %s with %f%% EER' % (best_additional_system, best_eer*100.))
        best_systems[protocol].append(best_additional_system)
        with open(best_systems_file, 'w') as f:
          f.write(best_additional_system)

        # fuse the scores of the best found machine
        logger.info('Fusing scores of the development and the evaluation set to files %s and %s' % (dev_result_file, eval_result_file))
        fuse_scores(best_machine, [dev_score_files[system] for system in best_systems[protocol]], dev_result_file)
        fuse_scores(best_machine, [eval_score_files[system] for system in best_systems[protocol]], eval_result_file)

      # compute the EER and HTER for the current files
      eer, hter = compute_performance(dev_result_file, eval_result_file)
      logger.info('Results for protocol %s and number of fused systems %d is: EER %f%%, HTER %f%%' % (protocol, i+1, eer*100, hter*100))
      results[protocol].append((eer, hter))


  # plot final results in a nice plot
  logger.info('Plotting the curves for protocol %s' % " and ".join(results.keys()))
  import matplotlib
  import matplotlib.pyplot as mpl
  from matplotlib.backends.backend_pdf import PdfPages
  # enable LaTeX interpreter
  matplotlib.rc('text', usetex=True)
  matplotlib.rc('font', family='serif')
  # increase the default font size
  matplotlib.rc('font', size=22)
  matplotlib.rcParams['xtick.major.pad'] = 24

  # create a multi-page PDF file
  pdf = PdfPages(args.plot_file)

  for protocol in results:
    # create a new figure
    figure = mpl.figure(figsize=(17,6))

    # select appropriate colors
    colors = [(.5,0,0,1), (0,0.5,0,1), (1,0,0,1), (0,1,0,1)]
    # arrange the results in a nice way
    x = range(len(best_systems[protocol]) * 3 + 2)
    y = [0] * len(x)
    c = [(0,0,0,0)] * len(x)
    index = 1
    for i,system in enumerate(best_systems[protocol]):
      y[index] = results[protocol][i][0] * 100.
      y[index+1] = results[protocol][i][1] * 100.
      c[index] = colors[system[0] == 'S']
      c[index+1] = colors[(system[0][0] == 'S') + 2]
      index += 3

    # generate a bar plot for the systems
    mpl.bar(x, y, color=c, align='center')

    # make the plot more beautiful
    mpl.axis((0, 3*len(best_systems[protocol]), 0, math.ceil(numpy.nanmax(y))))
    ticks = [1.5 + 3*i  for i in range(len(best_systems[protocol]))]
    mpl.xticks(ticks, best_systems[protocol], va='baseline', rotation=90)
    mpl.gca().set_position([0.1,0.12,.87,.85])
    mpl.ylabel('EER/HTER on MOBIO %s in \%%'%protocol)

    # dirty trick to have proper legends
    if 'face' in args.modality:
      mpl.bar(-1,0,color=colors[0],label=('EER (dev) of face system'))
      mpl.bar(-1,0,color=colors[2],label=('HTER (eval) of face system'))
    if 'speaker' in args.modality:
      mpl.bar(-1,0,color=colors[1],label=('EER (dev) of speaker system'))
      mpl.bar(-1,0,color=colors[3],label=('HTER (eval) of speaker system'))
    mpl.legend(loc='upper center', ncol=2, prop={'size':22})
    mpl.gca().yaxis.grid(True, color=(0.3,0.3,0.3))

    # add the figure for the current protocol to the PDF
    pdf.savefig(figure)

  # finally, write the pdf
  pdf.close()
  logger.info('Wrote plot file %s' % args.plot_file)

