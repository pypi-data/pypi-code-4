#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Jul 26 15:18:43 CEST 2013

"""Calculates Area Under EPSC curve
"""

import os
import sys
import bob
import numpy
import argparse

from ..utils import error_utils

def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('baseline_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (development set)')
  parser.add_argument('baseline_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (test set)')
  parser.add_argument('overlay_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; development set)')
  parser.add_argument('overlay_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; test set)')
      
  parser.add_argument('-p', '--points', metavar='INT', type=int, dest='points', default=100, help='Number of points for EPSC computation')
  parser.add_argument('--lb', '--l_bound', type=float, dest='l_bound', default=0, help='Value of lower bound of integration')
  parser.add_argument('--hb', '--h_bound', type=float, dest='h_bound', default=1, help='Value of higher bound of integration')
  parser.add_argument('-b', '--type-of-threshold', metavar='STR', type=str, dest='threshold', default="eer", help='Type of threshold', choices=('eer', 'hter'))
      
  args = parser.parse_args()
  
  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=args.points, criteria=args.threshold)
  aue = error_utils.calc_aue(base_neg, base_pos, over_neg, over_pos, weights, thrs, args.l_bound, args.h_bound)
  
  sys.stdout.write("AUE = %.4f \n" % aue)
  
  if __name__ == "__main__":
    main()

  

