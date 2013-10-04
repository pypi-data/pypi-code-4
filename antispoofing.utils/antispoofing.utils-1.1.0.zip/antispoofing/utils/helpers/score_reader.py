#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Thu 27 Sep 2012 13:01:44 CEST 

"""
Class that work with the scores

"""

import bob
import numpy

class ScoreReader:

  def __init__(self,files,inputDir):
    """
    " Receive a list of xbob.db.replay.File to return the scores
    """

    self.files = files
    self.inputDir = inputDir
  

  def __str__(self):
    return "%d video files " % len(self.files)


  def __reshape(self,scores):
    """
    A little hack.

    The motion package has the format x,1 and the lbptop has the format 1,x
    """
    if(scores.shape[1]==1):
      scores = numpy.reshape(scores,(scores.shape[1],scores.shape[0]))

    scores = numpy.reshape(scores,scores.shape[1])
    return scores


  def getScores(self,onlyValidScores=True, average=False, average_size=100):
    """
    Return a numpy.array with the scores of all xbob.db.replay.File

      onlyValidScores: Will return only the valid scores
      average: Will average a set of scores
      average_size: amount of acumulated scores in a video
    """

    #Finding the number of elements
    totalScores = 0
    if(average):
      totalScores = len(self.files)
    else:
      for f in self.files:
        fileName = str(f.make_path(self.inputDir,extension='.hdf5'))
        scores = bob.io.load(fileName)
        scores = self.__reshape(scores)

        if(onlyValidScores):
          scores = scores[(numpy.where(numpy.isnan(scores)==False))]

        totalScores =totalScores + len(scores)

    #allScores = numpy.zeros(shape=(1,totalScores))
    allScores = numpy.zeros(shape=(totalScores))

    offset = 0
    for f in self.files:
      fileName = str(f.make_path(self.inputDir,extension='.hdf5'))

      scores = bob.io.load(fileName)
      scores = self.__reshape(scores)

      if(onlyValidScores):
        scores = scores[(numpy.where(numpy.isnan(scores)==False))]

      if(average):
        scores = scores[(numpy.where(numpy.isnan(scores)==False))]#Removing nan
        #scores = numpy.average(scores)
        scores = numpy.sum(scores[0:average_size]) / float(average_size)
        scores = numpy.array([[scores]]) #reshaping

      #allScores=numpy.concatenate((allScores,scores),axis=1)
      #allScores[0,offset:offset+scores.shape[1]] = scores

      allScores[offset:offset+len(scores)] = numpy.reshape(scores,(len(scores)))
      offset = offset + len(scores)

    return allScores

