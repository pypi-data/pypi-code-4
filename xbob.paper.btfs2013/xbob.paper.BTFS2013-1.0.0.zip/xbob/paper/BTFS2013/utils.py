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


import os
import bob
import logging
logger = logging.getLogger('xbob.paper.BTFS2013')

def init_logger(verbosity_level):
  """Initializes the logging system and sets the given verbosity level."""
  level = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}[min(verbosity_level, 3)]
  logging.basicConfig(format="%(name)s@%(asctime)s -- %(levelname)s: %(message)s", level = level)


# A collection of names and their according abbreviation (sorted by EER on the male protocol)
ALGORITHMS = {
  # face algorithms
  'F-1' : 'UNILJ-ALP',
  'F-2' : 'GRADIANT',
  'F-3' : 'UC-HU',
  'F-4' : 'CPqD',
  'F-5' : 'TUT',
  'F-6' : 'UTS',
  'F-7' : 'Idiap',
  'F-8' : 'CDTA',
  'F-9' : 'baseline',

  # speaker algorithms
  'S-1' : 'Alpineon',
  'S-2' : 'L2F_EHU',
  'S-3' : 'Phonexia',
  'S-4' : 'GIAPSI',
  'S-5' : 'IDIAP',
  'S-6' : 'Mines-Telecom',
  'S-7' : 'L2F',
  'S-8' : 'EHU',
  'S-9' : 'CPqD',
  'S-10': 'CTDA',
  'S-11': 'RUN',
  'S-12': 'ATVS'
}


def collect_score_files(directory, modality, protocol, group, count = None):
  """Reads the score files for the given modality and protocol."""
  # get the number of files to read
  max_count = {'face' : 9, 'speaker' : 12}[modality]
  count = max_count if count is None or count > max_count else count

  # read the score files
  file_names = []
  systems = []
  logger.info("Collecting %d files for modality %s, protocol %s and group %s" % (count, modality, protocol, group))
  # read all desired score files
  for i in range(count):
    # compute raw score file name
    system = {'face':'F-%d', 'speaker' : 'S-%d'}[modality] % (i+1)
    score_file_name = os.path.join(directory, modality, ALGORITHMS[system], 'scores', '%s_%s.txt' % (group, protocol))
    file_names.append(score_file_name)
    systems.append(system)
    # check if the file exist
    if os.path.exists(score_file_name):
      logger.debug('Found score file %s' % score_file_name)
    else:
      logger.error('Could not find score file %s' % score_file_name)
  # return both the file name and the system shortcuts
  return file_names, systems


def fuse_scores(machine, score_files, output_file):
  """Fuses the selected score files with the given machine and writes the results to the given file."""
  # read all score files; these score files need to have the scores in the same order.
  score_file_lines = [bob.measure.load.four_column(f) for f in score_files]

  # get the first score file as reference
  first = score_file_lines[0]
  score_count = len(first)
  # create output file
  output = open(output_file, 'w')
  # iterate over the client/probe pairs
  for i in range(score_count):
    # get the raw scores of all systems for this specific client/probe pair
    raw_scores = [float(line[i][-1]) for line in score_file_lines]
    # fuse these scores into one value by using the given machine
    fused_score = machine(raw_scores)
    # write the fused score to file, using the reference client id, probe id and probe name
    output.write("%s %s %s %f\n" % (first[i][0] , first[i][1], first[i][2], fused_score))


def compute_performance(dev_file, eval_file):
  """Computes the EER and HTER performance for the given score files of the development and evaluation set."""
  # load the score files
  dev_scores = bob.measure.load.split_four_column(dev_file)
  eval_scores = bob.measure.load.split_four_column(eval_file)

  # compute a threshold based on the EER on the development set
  threshold = bob.measure.eer_threshold(dev_scores[0], dev_scores[1])
  # compute the EER on the development set
  far, frr = bob.measure.farfrr(dev_scores[0], dev_scores[1], threshold)
  eer = (far + frr) / 2.
  # compute the HTER on the evaluation set
  far, frr = bob.measure.farfrr(eval_scores[0], eval_scores[1], threshold)
  hter = (far + frr) / 2.

  return eer, hter



