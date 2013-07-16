#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Feb  8 09:10:01 CET 2013

"""
Compute the Q-statistics for a set of scores
"""

import argparse
import bob
import numpy
import os, sys

#from ..helpers import score_fusion_reader
from antispoofing.utils.db import *

from antispoofing.fusion.score_fusion.score_fusion import *
from antispoofing.fusion.readers.score_fusion_reader import *


def computeDecisions(scores,thresholds):
  decisions = numpy.zeros(scores.shape,dtype='bool')

  for i in range(len(thresholds)):
    decisions[:,i] = scores[:,i] >= thresholds[i]

  return decisions

def main():
 
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', type=str, dest='inputDir', nargs='+', default=INPUT_DIR, help='Base directory containing the scores (defaults to "%(default)s")')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  parser.add_argument('-a', '--average-scores', action='store_true', dest='average_scores', default=False, help='Use the average of scores')

  parser.add_argument('-s', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')

  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  inputDir   = args.inputDir

  average_scores     = args.average_scores
  average_size       = args.average_size


  if(len(inputDir) < 2):
    raise ValueError("Is necessary at least 2 path of scores")

  ########################
  #Querying the database
  ########################
  database = args.cls(args)
  trainRealObjects, trainAttackObjects = database.get_train_data()
  develRealObjects, develAttackObjects = database.get_devel_data()
  testRealObjects, testAttackObjects   = database.get_test_data()
  develObjects = develRealObjects + develAttackObjects

  #Loading the scores
  trainScores   = ScoreFusionReader(trainRealObjects+trainAttackObjects,inputDir).getConcatenetedScores(average=average_scores, average_size=average_size)

  develRealScores   = ScoreFusionReader(develRealObjects,inputDir).getConcatenetedScores(average=average_scores, average_size=average_size)
  develAttackScores = ScoreFusionReader(develAttackObjects,inputDir).getConcatenetedScores(average=average_scores, average_size=average_size)
  develScores       = ScoreFusionReader(develObjects,inputDir).getConcatenetedScores(average=average_scores, average_size=average_size)

  testScores   = ScoreFusionReader(testRealObjects+testAttackObjects,inputDir).getConcatenetedScores(average=average_scores, average_size=average_size)

  #Computing the thresholds for each countermeasure 
  thres = [] 
  for i in range(len(inputDir)):

    #Inverting the scores if needed
    if numpy.mean(develRealScores[:,i]) < numpy.mean(develAttackScores[:,i]):
      trainScores[:,i]     = trainScores[:,i] * -1
      develRealScores[:,i] = develRealScores[:,i] * -1; develAttackScores[:,i] = develAttackScores[:,i] * -1;
      develScores[:,i]     = develScores[:,i] * -1
      testScores[:,i]      = testScores[:,i] * -1

	
    t = bob.measure.eer_threshold(develAttackScores[:,i],develRealScores[:,i])
    thres.append(t)

  #Computing the classification decisions for each subset
  trainDecisions = computeDecisions(trainScores,thres)
  develDecisions = computeDecisions(develScores,thres)
  testDecisions  = computeDecisions(testScores,thres)


  #Computing the Q-Statistic for each subset
  qStatisticTrain = ScoreFusion.QAverage(trainDecisions)
  qStatisticDevel = ScoreFusion.QAverage(develDecisions)
  qStatisticTest = ScoreFusion.QAverage(testDecisions)

  print("Q-Statistic in the train set: " + str(qStatisticTrain))
  print("Q-Statistic in the devel set: " + str(qStatisticDevel))
  print("Q-Statistic in the test set: " + str(qStatisticTest))


  return 0

if __name__ == "__main__":
  main()
