#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue Feb 19 18:46:46 CET 2013


import os, sys
import argparse
import bob
import numpy

"""
Utilitary functions for easy packaging of features and other utilities
"""

def create_full_dataset(indir, objects):
  """Creates a full dataset matrix out of all the specified files.
  
  Returns:
   dataset - the full dataset matrix (Nan rows, which correspond to invalid frames are excluded)
   valid_frames - list of lists of valid frames for each video
   total_no_frames - list of total number of frames for each video
  """
  dataset = None
  valid_frames = [] # list of lists of valid frames of all the videos
  total_no_frames = [] # list of the total number of frames in each video
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    fvs = bob.io.load(filename)
    total_no_frames.append(fvs.shape[0])
    
    vf_truth_table = ~numpy.isnan(fvs).any(axis=1)
    
    vf_ind = [item for item in range(len(vf_truth_table)) if vf_truth_table[item].all() == True] # list of valid frames of this video
    
    valid_frames.append(vf_ind) 
    if dataset is None:
      dataset = fvs[vf_truth_table] # add up only the features of the valid frames
    else:
      dataset = numpy.append(dataset, fvs[vf_truth_table], axis = 0) 
  return dataset, valid_frames, total_no_frames

def average_scores(scores):
  """
  Compute the average of scores
  scores: Set of scores to normalize
  """
  av_scores = scores[(numpy.where(numpy.isnan(scores)==False))]#Removing nan
  return numpy.mean(av_scores)

def write_scores(valid_frames, total_frames, scores, objects, output_dir):
  """Writes the scores for each frame in the given set of videos (objects) into a separate file. Nan for invalid frames"""
  score_counter = 0 # counting the number of considered scores from the input score list
  for i in range(0, len(objects)):
    vf = valid_frames[i] # the valid frames for the current object
    file_scores = numpy.ndarray([1, total_frames[i]], dtype='float64')
    file_scores.fill(numpy.NAN)
    file_scores[0,vf] = scores[score_counter:score_counter+len(vf)].flatten() # all the scores belonging to the valid frames of this object
    score_counter += len(vf)
    objects[i].save(file_scores, output_dir, '.hdf5')
    
    
def pervideo_scores(valid_frames, total_frames, scores, objects):
  """Averages the scores of all the frames in the video and writes the averaged score."""
  accumulated_scores = []
  score_counter = 0 # counting the number of considered scores from the input score list
  for i in range(0, len(objects)):
    vf = valid_frames[i] # the valid frames for the current object
    file_scores = numpy.ndarray([1, total_frames[i]], dtype='float64')
    file_scores.fill(numpy.NAN)
    file_scores[0,vf] = scores[score_counter:score_counter+len(vf)].flatten() # all the scores belonging to the valid frames of this object
    score_counter += len(vf)
    accumulated_scores.append([objects[i].make_path(),average_scores(file_scores)])

  return accumulated_scores
      
    
