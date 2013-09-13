#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Mar  8 17:28:51 CET 2013

"""Plot different types of plots (figures) for a particular fused face verification and anti-spoofing algorithm. Here the results of only combination of face verification and anti-spoofing algorithms are given! No comparison between different fusion algorithms is possible with this script.
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob
import numpy
import argparse

import matplotlib.font_manager as fm

from ..utils import error_utils
      

def epc(dev_negatives, dev_positives, test_negatives, test_positives, points):
  """Reproduces the bob.measure.epc() functionality, but returns the
  thresholds on the 3rd column of the input data."""

  retval = numpy.ndarray((points, 3), 'float64')
  step = 1./(float(points)-1.)

  for i in range(points):
    retval[i,0] = i*step
    retval[i,2] = bob.measure.min_weighted_error_rate_threshold(dev_negatives,
        dev_positives, retval[i,0])
    retval[i,1] = sum(bob.measure.farfrr(test_negatives, test_positives, retval[i,2]))/2.

  return retval

def epc_errors(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds):
  """For a numpy.ndarray of thresholds, gives the appropriate error rates: FRR, FAR (impostors), HTER (licit), total FAR, total HTER, ASP"""

  retval = numpy.ndarray((numpy.array(thresholds).size, 6), 'float64')

  farfrr_licit = [bob.measure.farfrr(licit_neg, licit_pos, thres) for thres in thresholds] # calculate test frr @ EER (licit protocol)
  farfrr_spoof = [bob.measure.farfrr(spoof_neg, spoof_pos, thres) for thres in thresholds] # calculate test frr @ EER (spoof protocol)
  farfrr_total = [bob.measure.farfrr(numpy.append(licit_neg, spoof_neg), numpy.append(licit_pos, spoof_pos), thres) for thres in thresholds]
  frr = [x[1] for x in farfrr_licit]
  far = [x[0] for x in farfrr_licit]
  hter_fv = [(x[1] + x[0]) / 2 for x in farfrr_licit]
  far_total = [x[0] for x in farfrr_total]
  hter_total = [(x[1] + x[0])/2 for x in farfrr_total]
  asp = [x[0] for x in farfrr_spoof]

  retval[:,0] = numpy.array(frr[:])
  retval[:,1] = numpy.array(far[:])
  retval[:,2] = numpy.array(hter_fv[:])
  retval[:,3] = numpy.array(far_total[:])
  retval[:,4] = numpy.array(hter_total[:])
  retval[:,5] = numpy.array(asp[:])  

  return retval

def epc_thresholds(dev_negatives, dev_positives, points):
  """Returns a list of thresholds for EPC curve"""

  step = 1./(float(points)-1.)
  retval = [bob.measure.min_weighted_error_rate_threshold(dev_negatives, dev_positives, i*step) for i in range(points)]
  steps = [i*step for i in range(points)]
  return retval, steps


def pass_rate(threshold, attacks):
  """Calculates the rate of attacks that are after a certain threshold"""

  return sum(1 for i in attacks if i >= threshold)/float(attacks.size)

def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('licit_dev', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification for LICIT protocol (development set)')
  parser.add_argument('licit_test', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification for LICIT protocol (test set)')
  parser.add_argument('spoof_dev', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives i.e. SPOOF protocol (spoofing attacks; development set)')
  parser.add_argument('spoof_test', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives i.e. SPOOF protocol (spoofing attacks; test set)')
  parser.add_argument('licit_dev_fvas', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the fused face verification + cm for LICIT protocol (development set)')
  parser.add_argument('licit_test_fvas', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the fused face verification + cm for LICIT protocol(test set)')
  parser.add_argument('spoof_dev_fvas', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the fused face verification + cm overlaid negatives i.e. SPOOF protocol (spoofing attacks + cm; development set)')
  parser.add_argument('spoof_test_fvas', metavar='FILE', type=str, default="", help='Name of the scores file (4-column) containing the scores for the fused face verification + cm overlaid negatives i.e. SPOOF protocol (spoofing attacks + cm; test set)')
  parser.add_argument('-p', '--protocol', metavar='STR', type=str, dest='protocol', default="", help='Legend that will be used for the overlaied negatives (spoofing attacks)')
  parser.add_argument('-t', '--title', metavar='STR', type=str, dest='title', default="", help='Plot title')
  #parser.add_argument('--fv', '--faceverif', metavar='STR', type=str, dest='faceverif', default="", help='The face verification algorithm')
  #parser.add_argument('--as', '--antispoofing', metavar='STR', type=str, dest='antispoofing', default="", help='The anti-spoofing algorithm')
  #parser.add_argument('-f', '--fusion_alg', metavar='STR', type=str, dest='fusionalg', default="", help='The fusion algorithm')
  parser.add_argument('-i', '--plots_to_include', metavar='STR', type=int, dest='plotstoinclude', default=[1,2,3,4,5,6,7,8,9], help='The plots that will be included in the output pdf file', nargs='+')
  parser.add_argument('-o', '--output', metavar='FILE', type=str, default='plots.pdf', dest='output', help='Set the name of the output file (defaults to "%(default)s")')

  args = parser.parse_args()

  if not args.title: 
    args.title = os.path.splitext(os.path.basename(args.licit_test))[0]
  if not args.protocol: 
    args.protocol = os.path.splitext(os.path.basename(args.licit_test))[0]

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.licit_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.spoof_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.licit_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.spoof_dev)

  [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(args.licit_test_fvas)
  [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(args.spoof_test_fvas)
  [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(args.licit_dev_fvas)
  [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(args.spoof_dev_fvas)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)
  
  
  
