#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Sat Feb  9 15:53:48 CET 2013

"""Calculates GLCM features of the frames in Replay-Attack database. The input files are hdf5 format files (of cropped faces).
"""

import os, sys
import argparse
import bob
import numpy
import math
import string

from antispoofing.utils.db import *

properties_list = ["autocorrelation", "contrast", "correlation matlab", "correlation", "cluster prominance", "cluster shade", "dissimilarity", "angular second moment", "entropy", "homogeneity", "inverse difference moment", "maximum probability", "variance", "sum average", "sum variance", "sum entropy", "difference variance", "difference entropy", "information measure of correlation 1", "information measure of correlation 2", "inverse difference normalized", "inverse difference moment normalized"]



def shimage(normbox):
  ''' Shows an image on the screen (just for debugging purposes)'''
  import numpy as np
  ar = np.empty((normbox.shape[0], normbox.shape[1]), dtype = 'uint8')
  for i in range(0, normbox.shape[0]):
    for j in range(0, normbox.shape[1]):
      ar[i,j] = normbox[i,j]

  
  import matplotlib.cm as cm
  import matplotlib.mlab as mlab
  import matplotlib.pyplot as plt
  im = plt.imshow(ar, cmap = cm.gray, aspect='equal')
  plt.show()



def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'glcm_features')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-d', '--directory', dest="directory", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-m', dest='matlab_compatible', action='store_true', default=False, help='If set, the features will be computed on a Matlab compatible GLCM')

  #######
  # Database especific configuration
  #######
  #Database.create_parser(parser)
  
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  
  ########################
  #Querying the database
  ########################
  database = args.cls(args)
  realObjects, attackObjects = database.get_all_data()
  
  args_keys = vars(args)
  icb2013 = False
  if 'icb2013' in args_keys.keys():
    if(args.icb2013):
      icb2013 = True
  
  
  if icb2013:
    process = realObjects[-480:] # taking the anonymized test data from all the returned real_objects only
  else:  
    process = realObjects + attackObjects 

  counter = 0
  
  # prepare the GLCM operators
  if not args. matlab_compatible:
    glcm_op = bob.ip.GLCM('uint8', num_levels=8)
  else:
    glcm_op = bob.ip.GLCM('uint8', numpy.array([0,19,55,92,128,164,201,237], dtype='uint8')) # thresholds selected according to matlab quantization thresholds
  offset = numpy.array([[0,1],[1,1],[1,0]], dtype='int32') # additional offset to test: [1,-1]
  glcm_op.offset = offset
  glcp_prop_op = bob.ip.GLCMProp()
  
  # process each video
  for obj in process:
    counter += 1

    indata = bob.io.load(obj.make_path(directory = args.inputdir, extension='.hdf5'))    
    
    featdata = numpy.ndarray((0, len(properties_list)*len(offset)), 'float64') # the numpy.ndarray, each row is the feature vector of one frame. The number of features is the lenght of the properties list times the number of offsets

    numvf = 0 # number of valid frames in the video (will be smaller then the total number of frames if a face is not detected or a very small face is detected in a frame when face lbp are calculated   
   
    sys.stdout.write("Processing file %s (%d frames) [%d/%d] " % (obj.make_path(),
      indata.shape[0], counter, len(process)))
   
    for k in range(0, indata.shape[0]): 
      if numpy.all(numpy.isnan(indata[k,:,:])):
        feat = numpy.ndarray((1, len(properties_list)*len(offset)), 'float64')
        feat.fill(numpy.NAN)
      else:
        inframe = indata[k,:,:]
        
       
        '''
        gauss = bob.ip.Gaussian()
        inframe_gauss = gauss(inframe) 
        inframe_lapl = bob.ip.laplacian_avg_hs(inframe)
        inframe = indata[k,:,:] - inframe_lapl + 128
        '''
        
        inframe_ = inframe + 0.5
        inframe_ = numpy.floor(inframe_)
        inframe_uint = numpy.cast['uint8'](inframe_) # GLCM requires 'uint8' input
        #import ipdb; ipdb.set_trace()
        #shimage(inframe_uint)
        
        glcm = glcm_op(inframe_uint)
      
        glcm_prop = glcp_prop_op.properties_by_name(glcm, properties_list)
        feat = [x.tolist() for x in glcm_prop] # we get list of lists of features
        feat = numpy.array(reduce(lambda x,y: x+y,feat))
        sys.stdout.write('.')
        sys.stdout.flush()
        
      featdata = numpy.append(featdata, feat.reshape([1, feat.size]), axis=0)
    
    sys.stdout.write('\n')
    sys.stdout.flush()
    # saves the output
    obj.save(featdata, directory = args.directory, extension='.hdf5')

  return 0

if __name__ == "__main__":
  main()
