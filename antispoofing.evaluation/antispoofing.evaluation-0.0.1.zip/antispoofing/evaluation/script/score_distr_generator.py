#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Feb 18 14:06:01 CET 2013

""" Generates random scores for three types of verification attempts: genuine users, zero-effort impostors and spoofing attacks and writes them into 4-column score files for so called licit and spoof scenario. The scores are generated using Gaussian distribution whose mean is an input parameter. The generated scores can be used as hypothetical datasets.
"""

import os
import sys
import bob
import numpy
import argparse

from ..utils import *

NUM_REAL_ACCESS = 5000
NUM_IMPOSTORS = 5000
NUM_SPOOF = 5000


def gen_score_distr(mean_real = 2, mean_imp = 0, mean_spoof = 1, sigma_real=1, sigma_imp=1, sigma_spoof=1):
  """ Method that generates three different score distributions using Gaussian distribution, given their means and variances as input parameters
  """
  mt = bob.core.random.mt19937()  # initialise the random number generator

  real_generator = bob.core.random.normal_float32(mean_real, sigma_real)
  imp_generator = bob.core.random.normal_float32(mean_imp, sigma_imp)
  spoof_generator = bob.core.random.normal_float32(mean_spoof, sigma_spoof)
  
  real_scores = [real_generator(mt) for i in range(NUM_REAL_ACCESS)]
  imp_scores = [imp_generator(mt) for i in range(NUM_IMPOSTORS)]
  spoof_scores = [spoof_generator(mt) for i in range(NUM_SPOOF)]
  
  return real_scores, imp_scores, spoof_scores
  

def write_scores_to_file(pos, neg, filename):
  """ Method that writes score distributions into 4-column score files. For the format of the 4-column score files, please refer to Bob's documentation. 
  
  Keyword parameters:
  
    pos: list of scores for positive samples to be written
    neg: list of scores for negative samples to be written
    filename: name of the file to be written
  """
  tbl = []
  for i in pos:
    tbl.append('x x foo %f\n' % i)
  for i in neg:
    tbl.append('x y foo %f\n' % i)     
  
  txt = ''.join([k+'\n' for k in tbl])

  # write the results to a file 
  ensure_dir(filename)
  tf = open(filename, 'w')
  tf.write(txt)


def main():
  
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('-d', '--outdir', dest = 'outdir', metavar='DIR', type=str,
      default="hpt_scores", help='The directory where the hypothetical score distributions are to be written')
  parser.add_argument('-r', '--mean_real', metavar='INT', type=int, dest='mean_real', default="10", help='Mean for real access score distribution')
  parser.add_argument('-i', '--mean_imp', metavar='INT', type=int, dest='mean_imp', default="0", help='Mean for impostors score distribution')
  parser.add_argument('-s', '--mean_spoof', metavar='INT', type=int, dest='mean_spoof', default="5", help='Mean for spoofing attacks score distribution')

  args = parser.parse_args()

  # Generate the data  
  real_dev, imp_dev, spoof_dev = gen_score_distr(args.mean_real, args.mean_imp, args.mean_spoof)
  real_test, imp_test, spoof_test = gen_score_distr(args.mean_real, args.mean_imp, args.mean_spoof)

  # Write the data into files
  write_scores_to_file(real_dev, imp_dev, os.path.join(args.outdir, 'licit', 'scores-dev'))
  write_scores_to_file(real_test, imp_test, os.path.join(args.outdir, 'licit', 'scores-test'))
  write_scores_to_file(real_dev, spoof_dev, os.path.join(args.outdir, 'spoof', 'scores-dev'))
  write_scores_to_file(real_test, spoof_test, os.path.join(args.outdir, 'spoof', 'scores-test'))
  
if __name__ == '__main__':
  main()  
  
  
