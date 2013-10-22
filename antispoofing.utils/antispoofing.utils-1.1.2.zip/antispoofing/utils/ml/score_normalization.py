#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Sep 27 17:04:09 CEST 2012

import bob
import numpy


class ScoreNormalization:
  """
  Class that implements some score normalization algorithms
  """

  def __init__(self, scores=None):
    """
    " Constructor
    " @param scores set of scores to help in the normalization
    """

    if scores!= None:
      self.mins = numpy.min(scores,axis=0)
      self.maxs = numpy.max(scores,axis=0)
    
      self.avg =  numpy.average(scores,axis=0)
      self.std  = numpy.std(scores,axis=0)

      self.totalScores = len(scores)
        

  def __str__(self): 
    string = ''
    if hasattr(self, 'totalScores'):      
      string =  "%d Scores \n" + "min = " + str(self.mins) + "\nmax = " + str(self.maxs) + "\navg = " + str(self.avg) + "\nstd = " + str(self.std)
      '''string =  "%d Scores \n min=%.2f \n max=%.2f \n Average=%.2f \n Standard Deviation=%.2f " % \
              (self.totalScores, 
              self.mins, 
              self.maxs, 
              self.avg, 
              self.std,
             )'''
    return string

  def set_norm_params(self, mins, maxs, avg, std):
    self.mins = mins
    self.maxs = maxs
    self.avg = avg
    self.std = std
    self.totalScores = 0


  def calculateZNorm(self,scores):
    """
    Make the ZNorm score normalization
 
    @param scores numpy.array to be normalized
    @return numpy.array with the normalized scores
    """

    return numpy.divide((scores - self.avg),self.std)

  def inverseZNorm(self, normscores, dim):
    """
    De-normalize the input cores with ZNorm score normalization
 
    @param scores numpy.array to be de-normalized
    @dim tuple of the first and last dimension to be considered 
    @return numpy.array with de-normalized scores
    """
    begindim = dim[0]; enddim = dim[1] + 1
    return self.std[begindim:enddim] * normscores[:,begindim:enddim] + self.avg[begindim:enddim]


  def calculateMinMaxNorm(self,scores,lowerBound = -1, upperBound = 1):
    """
    Normalize the score in an specific interval
 
    @param scores numpy.array to be normalized
    @param lowBound The lower bound
    @param upperBound The upper bound

    @return numpy.array with the normalized scores.
    """

    denom = self.maxs - self.mins
    normalizedScores = (upperBound - lowerBound) * (scores - self.mins) / denom + lowerBound

    return normalizedScores

