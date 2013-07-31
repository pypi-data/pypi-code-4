#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Feb  8 09:10:01 CET 2013

"""
Countermeasure that takes account the area of the face bounding box.
"""

import argparse
import bob
import numpy
import os, sys
import string

#from ..helpers import score_fusion_reader
from antispoofing.utils.db import *
import antispoofing.utils
from antispoofing.utils.faceloc import *

def loadBB(objects,database,inputDir):

  area = numpy.array([])

  # processing each video
  for index, obj in enumerate(objects):

    #Loading the face locations
    if string.find(database.short_description(), "CASIA") != -1:
      flocfile = obj.facefile()
    else:
      flocfile = obj.facefile(inputDir)

    #Loading the file
    filename = str(obj.videofile(inputDir))

    #Loading the video
    input = bob.io.VideoReader(filename)
    locations = preprocess_detections(flocfile,input.number_of_frames)

    for bbx in locations:
      if bbx != None:
        a = bbx.width * bbx.height
        area = numpy.concatenate((area,[a]))

  return area
	

def main():
 
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', type=str, dest='inputDir', default=INPUT_DIR, help='Base directory of the database (defaults to "%(default)s")')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  inputDir   = args.inputDir

  ########################
  #Querying the database
  ########################
  database = args.cls(args)
  trainRealObjects, trainAttackObjects = database.get_train_data()
  develRealObjects, develAttackObjects = database.get_devel_data()
  testRealObjects, testAttackObjects   = database.get_test_data()

  #Computing area
  trainRealArea = loadBB(trainRealObjects,database,inputDir)
  trainAttackArea = loadBB(trainAttackObjects,database,inputDir)

  develRealArea = loadBB(develRealObjects,database,inputDir)
  develAttackArea = loadBB(develAttackObjects,database,inputDir)
  
  testRealArea = loadBB(testRealObjects,database,inputDir)
  testAttackArea = loadBB(testAttackObjects,database,inputDir)

  if numpy.mean(develRealArea) < numpy.mean(develAttackArea):
    trainRealArea = trainRealArea * -1; trainAttackArea = trainAttackArea * -1
    develRealArea = develRealArea * -1; develAttackArea = develAttackArea * -1
    testRealArea = testRealArea * -1; testAttackArea = testAttackArea * -1


  thres = bob.measure.eer_threshold(develAttackArea, develRealArea)

  FAR, FRR = bob.measure.farfrr(trainAttackArea, trainRealArea, thres)
  HTER_train = (FAR+FRR)/2.

  FAR, FRR = bob.measure.farfrr(develAttackArea, develRealArea, thres)
  HTER_dev = (FAR+FRR)/2.

  FAR, FRR = bob.measure.farfrr(testAttackArea, testRealArea, thres)
  HTER_test = (FAR+FRR)/2.


  print("HTER - train: " + str(HTER_train))
  print("HTER - devel: " + str(HTER_dev))
  print("HTER - test: " + str(HTER_test))
  
  

  return 0

if __name__ == "__main__":
  main()
