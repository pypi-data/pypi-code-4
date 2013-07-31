#!/usr/bin/env /idiap/group/torch5spro/nightlies/last/install/linux-x86_64-release/bin/python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Dec  3 19:10:36 CET 2012

''' This script crops the faces of the videos in REPLAY-ATTACK and creates a new video with only cropped face'''

import bob, numpy, random, os
import sys
import string
from itertools import chain

from antispoofing.utils.db import *
from antispoofing.utils.faceloc import *
from antispoofing.utils.helpers import *

INDIR='/idiap/group/replay/database/protocols/replayattack-database/'
OUTDIR='/idiap/temp/ichingo/replay-attack-croppedfaces/hdf5'

def shimage(normbox, isgrey=False):
  ''' Shows an image on the screen (just for debugging purposes)'''
  
  import numpy as np
  import matplotlib.cm as cm
  import matplotlib.mlab as mlab
  import matplotlib.pyplot as plt
  
  #import ipdb; ipdb.set_trace()
  if isgrey==True:
    ar = np.empty((normbox.shape[0], normbox.shape[1]), dtype = 'uint8')
    for i in range(0, normbox.shape[0]):
      for j in range(0, normbox.shape[1]):
        ar[i,j] = normbox[i,j]
    im = plt.imshow(ar, cmap = cm.gray, aspect='equal')
  else:  
    im = plt.imshow(normbox, aspect='equal')
  plt.show()

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
      
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INDIR, help='Base directory containing the files to be treated by this procedure (defaults to "%(default)s")')
  
  parser.add_argument('-d', '--frameoutputdir', metavar='DIR', type=str, default=OUTDIR, help='Directory where the extracted frames will be stored')

  parser.add_argument('-n', '--normface-size', dest="normfacesize", default=64, type=int, help="this is the size of the normalized face box if face  normalization is used (defaults to '%(default)s')")

  parser.add_argument('-t', '--output-type', dest='outputtype', default='.hdf5', type=str, help="the type of output file (defaults to '%(default)s')", choices=('.hdf5', '.avi'))
  
  parser.add_argument('--it', '--input-type', dest='inputtype', default='.hdf5', type=str, help="the type of input files (defaults to '%(default)s')", choices=('.hdf5', '.mov'))

  parser.add_argument('--ff', '--facesize_filter', dest="facesize_filter", default=0, type=int, help="all the frames with faces smaller then this number, will be discarded (defaults to '%(default)s')")  
  parser.add_argument('-f', '--force', dest='force', action='store_true', default=False, help='Force to erase former data if already exists')

  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  #Querying the database
  database = args.cls(args)
  realObjects, attackObjects = database.get_all_data()
  
  args_keys = vars(args)
  icb2013 = False
  if 'icb2013' in args_keys.keys():
    if(args.icb2013):
      icb2013 = True
  
  
  if icb2013:
    objects = realObjects[-480:] # taking the anonymized test data from all the returned real_objects only
  else:  
    objects = realObjects + attackObjects 

  counter = 0
  for obj in objects:
    counter +=1
    
    sys.stdout.write("Processing file '%s' (%d/%d)" % (obj.make_path(), counter, len(objects)))
    sys.stdout.flush()
    
    # bootstraps video reader for client
    if args.inputtype == '.hdf5':
      video = bob.io.load(obj.make_path(directory=args.inputdir, extension='.hdf5'))
    else:  
      video = bob.io.VideoReader(str(obj.videofile(directory=args.inputdir))) 
    
    if args.inputtype == '.hdf5':
      numframes = video.shape[0]
    else:
      numframes = video.number_of_frames  

    # loads face locations - roll localization
    if string.find(database.short_description(), "CASIA") != -1:
      flocfile = obj.facefile()
    else:
      flocfile = obj.facefile(args.inputdir)
    locations = preprocess_detections(flocfile,numframes,facesize_filter=args.facesize_filter)
    
    outputfilename = obj.make_path(args.frameoutputdir, args.outputtype)
    ensure_dir(os.path.dirname(outputfilename))
    
    if args.outputtype == '.avi': # the output is a video file
      vout = bob.io.VideoWriter(outputfilename, args.normfacesize, args.normfacesize, framerate=video.frame_rate)
    else: 
      vout = numpy.ndarray((numframes, args.normfacesize, args.normfacesize), 'float64')      
    
    for frame_index in range(0,numframes): #frame in enumerate(video):
      if args.inputtype == '.hdf5':
        frame = numpy.transpose(video[frame_index,:,:,:], [2,0,1])
      else:
        frame = video[frame_index]
    
      frame_f = bob.ip.rgb_to_gray(frame)
        
      bbx = locations[frame_index]
      sz = args.normfacesize
  
      if bbx and bbx.is_valid() and bbx.height > args.facesize_filter:
        cutframe = frame_f[bbx.y:(bbx.y+bbx.height),bbx.x:(bbx.x+bbx.width)] # cutting the box region
        tempbbx = numpy.ndarray((sz, sz), 'float64')
        normbbx = numpy.ndarray((3, sz, sz), 'uint8')
        #tempbbx = numpy.ndarray((3, sz, sz), 'float64')
        #normbbx = numpy.ndarray((3, sz, sz), 'uint8')
        bob.ip.scale(cutframe, tempbbx) # normalization
        tempbbx_ = tempbbx + 0.5
        tempbbx_ = numpy.floor(tempbbx_)
        normbbx[:,:,:] = numpy.cast['uint8'](tempbbx_)
      else:
        if args.outputtype == '.avi': # the output is a video file
          normbbx = numpy.ndarray((3, sz, sz), 'uint8')      
          normbbx.fill(0)
        else:
          tempbbx.fill(numpy.NAN)

      if args.outputtype == '.avi': # the output is a video file
        vout.append(normbbx) #norm_bbx
      else:
        vout[frame_index,:,:] = tempbbx
        
      sys.stdout.write('.')
      sys.stdout.flush()
      
    if args.outputtype == '.avi': # the output is a video file
      vout.close()  
    else:
      obj.save(vout, directory = args.frameoutputdir, extension=args.outputtype)

    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
  main()


