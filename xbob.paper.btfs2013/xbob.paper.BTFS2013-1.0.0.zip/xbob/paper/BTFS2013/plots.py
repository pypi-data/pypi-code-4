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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# a stacked bar plot with errorbars
import sys
import os
import bob
import numpy
import math

from .utils import logger, init_logger, compute_performance, ALGORITHMS, fuse_scores

# plotting stuff
import matplotlib
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=22)
matplotlib.rcParams['xtick.major.pad'] = 24



def parse_command_line(command_line_options):
  """Defines the command line parameters that are accepted."""

  import argparse
  parser = argparse.ArgumentParser(description='Plots several curves and plots', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--data-directory', required=True, help = 'The directory where the score files can be found.')
  parser.add_argument('-u', '--unimodal-directory', default='fused/unimodal', help = 'The directory where the score files of the uni-modal fusion (i.e., the result of bin/unimodal.py) can can be found.')
  parser.add_argument('-b', '--bimodal-directory', default='fused/bimodal', help = 'The directory where the score files of the bi-modal fusion (i.e., the result of bin/bimodal.py) can can be found.')
  parser.add_argument('-w', '--plot-file', default = 'plots.pdf', help = 'The pdf file where the graphics should be plotted into.')

  parser.add_argument('-f', '--force', action='store_true', help = 'Force the single best bimodal files to be re-created even if they already exist.')
  parser.add_argument('-v', '--verbose', action='count', default=0, help = 'Increase the verbosity level from ERROR (0) to WARNING (1), INFO (2) and DEBUG (3).')

  args = parser.parse_args(command_line_options)

  # set logging level
  init_logger(args.verbose)

  return args


def plot_det(pdf, files, labels):
  """Plots the DET for the given files and the given labels."""
  # prepare det plot
  det_list = [1e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 4e-1, 5e-1]
  cmap = mpl.cm.get_cmap(name='hsv')
  colors = [(.5,0,0,1), (1,0,0,1), (0,0.5,0,1), (0,1,0,1), (0,0,0.5,1), (0,0,1,1)]
  markers = ('-x', '-+', '-v', '-^', '-d', '-s')
  # read score files
  logger.debug('Loading %d score files' % len(files))
  scores = [bob.measure.load.split_four_column(f) for f in files]

  # plot det
  figure = mpl.figure(figsize=(8.2,8))
  for i in range(len(scores)):
    far, frr = bob.measure.det(scores[i][0], scores[i][1], 1000)
    mpl.plot(far, frr, markers[i], color = colors[i], lw=3, ms=10, mew=3, mec = colors[i], label=labels[i], markevery=50)

  # set axis labels
  ticks = [bob.measure.ppndf(d) for d in det_list]
  tick_labels = [("%.5f" % (d*100)).rstrip('0').rstrip('.') for d in det_list]
  mpl.xticks(ticks, tick_labels, fontsize=18, va='baseline')
  mpl.yticks(ticks, tick_labels, fontsize=18)
  mpl.axis((ticks[0], ticks[-1], ticks[0], ticks[-1]))

  # beautify plot
  mpl.xlabel('False Acceptance Rate (\%)', fontsize=22)
  mpl.ylabel('False Rejection Rate (\%)', fontsize=22)
  mpl.grid(True, color=(0.3,0.3,0.3))
  legend_handle = mpl.legend(ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, 1.15))

  # append the plot to the pdf
  pdf.savefig(figure,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])


def comparison_plot(pdf, results, labels):
  """Plots the given set of results to the given pdf in a bar-plot with proper alignment."""
  # create new figure
  figure = mpl.figure(figsize=(11,6))

  # get enough colors for the 8 or 9 different types of results
  colors = [(0.5,0,0,1), (1,0,0,1), (0,0.5,0,1), (0,1,0,1), (0,0,0.5,1), (0,0,1,1), 'LightGrey', 'DarkGray', 'Black']
  # re-arrange results
  gap = 6
  count = len(results)
  x = range(count * 2 + gap + 1)
  y = [0] * len(x)
  c = [(0,0,0,0)] * len(x)

  for i in range(1, count+1):
    y[i] = results[i-1][0]
    c[i] = colors[i-1]
    y[i+count+gap] = results[i-1][1]
    c[i+count+gap] = colors[i-1]

  mpl.bar(x, y, 0.8, color=c, align='center',label=None)

  # dirty trick to have proper legends
  for i in range(count):
    mpl.bar(-1,0,color=colors[i],label=labels[i])
  mpl.legend(loc='upper center', ncol=3, prop = {'size':16})

  # beautify the plot
  mpl.ylabel('HTER on MOBIO evaluation set in \%%', fontsize=18 )
  mpl.xticks((count/2.+0.5,count/2.+count+gap+0.5), ('\emph{male}', '\emph{female}'), fontsize=18, va='baseline' )
  mpl.yticks(numpy.arange(0,17.5,2.5), [str(int(l)) if math.floor(l)==l else "" for l in numpy.arange(0,27.5,2.5) ], fontsize=18 )
  mpl.axis((-.5, len(x)+.5, 0, 18))
  mpl.gca().yaxis.grid(True, color=(0.3,0.3,0.3))

  # append the plot to the pdf
  pdf.savefig(figure)


def main(command_line_options=None):
  """Generates several plots for the paper."""
  # get the command line options
  args = parse_command_line(command_line_options)

  dev_files = {}
  eval_files = {}
  names = ['best face', 'fusion face', 'best speaker', 'fusion speaker', 'best bi-modal', 'fusion bi-modal']
  # get the results of all desired curves
  for protocol in ('male', 'female'):
    # collect the score files for the protocol; we use the locations where the other scripts have generated the fusion files
    best_single_face = [os.path.join(args.data_directory, 'face', ALGORITHMS['F-1'], 'scores', '%s_%s.txt' % (group, protocol)) for group in ('dev', 'eval')]
    best_single_speaker = [os.path.join(args.data_directory, 'speaker', ALGORITHMS['S-1'], 'scores', '%s_%s.txt' % (group, protocol)) for group in ('dev', 'eval')]
    best_fused_face = [os.path.join(args.unimodal_directory, 'face', '%s_%s_best_9.txt' % (protocol, group)) for group in ('dev', 'eval')]
    best_fused_speaker = [os.path.join(args.unimodal_directory, 'speaker', '%s_%s_best_12.txt' % (protocol, group)) for group in ('dev', 'eval')]
    best_single_bimodal = [os.path.join(args.bimodal_directory, '%s_%s_bimodal.txt' % (protocol, group)) for group in ('dev', 'eval')]
    best_fused_bimodal = [os.path.join(args.bimodal_directory, '%s_%s_best_21.txt' % (protocol, group)) for group in ('dev', 'eval')]

    # split into  development set and evaluation set files
    dev_files[protocol] = [f[0] for f in (best_single_face, best_fused_face, best_single_speaker, best_fused_speaker, best_single_bimodal, best_fused_bimodal)]
    eval_files[protocol] = [f[1] for f in (best_single_face, best_fused_face, best_single_speaker, best_fused_speaker, best_single_bimodal, best_fused_bimodal)]

    # check if the best_single_bimodal files exist
    if not os.path.exists(best_single_bimodal[0]) or not os.path.exists(best_single_bimodal[1]) or args.force:
      logger.info('Fusing the best face and the best speaker recognition algorithm for protocol %s' % protocol)
      # perform bi-modal fusion of the best single systems
      face_scores = bob.measure.load.split_four_column(best_single_face[0])
      speaker_scores = bob.measure.load.split_four_column(best_single_speaker[0])
      negatives = numpy.vstack([face_scores[0], speaker_scores[0]]).T
      positives = numpy.vstack([face_scores[1], speaker_scores[1]]).T
      # train a linear machine that will do the score fusion
      # using conjugated gradient logistic regression
      trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
      machine = trainer.train(negatives, positives)
      # fuse the scores and write the files
      logger.debug('Fusing scores for the development set')
      fuse_scores(machine, [best_single_face[0], best_single_speaker[0]], best_single_bimodal[0])
      logger.debug('Fusing scores for the evaluation set')
      fuse_scores(machine, [best_single_face[1], best_single_speaker[1]], best_single_bimodal[1])


  # compute the HTER results for male and female
  hters = []
  for i in range(len(names)):
    # we are not interested in the EER on the development set, so we just ignore them
    _, hter_male = compute_performance(dev_files['male'][i], eval_files['male'][i])
    _, hter_female = compute_performance(dev_files['female'][i], eval_files['female'][i])
    hters.append((hter_male*100., hter_female*100.))

  # append some reference results
  names.append('McCool et al. [11]')
  hters.append((11.9, 13.3)) # McCool et al.
  names.append('Motlicek et al. [34]')
  hters.append((2.6, 9.7)) # Motlicek et al.

  # this paper of us is under review and might be added as well
#  names.append('Khoury et al. [38]')
#  hters.append((1.9, 6.3)) # Khoury et al


  # open multipage PDF file
  pdf = PdfPages(args.plot_file)

  # plot the det curves for the evaluation sets
  logger.info('Generating DET plots')
  plot_det(pdf, eval_files['male'], names)
  plot_det(pdf, eval_files['female'], names)

  # plot the comparison of HTER on male and female
  logger.info('Generating comparison plots')
  comparison_plot(pdf, hters, names)

  # write the PDF
  pdf.close()
  logger.info('Wrote PDF file %s' % args.plot_file)

