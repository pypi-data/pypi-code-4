#!/idiap/group/torch5spro/nightlies/last/install/linux-x86_64-debug/bin/ipython
#Nesli Erdogmus <nesli.erdogmus@idiap.ch>
#Thu Jul 11 16:27:33 CET 2013

"""Calculates the frame accumulated and then averaged LBP histogram of the normalized faces in the videos in the 3D MASK ATTACK database. The result is the average LBP histogram over all the frames of the video. Different types of LBP operators are supported. The histograms can be computed for a subset of the videos in the database (using the protocols in the database). The output is a single .hdf5 file for each video.
"""

import os, sys
import argparse
import bob
import numpy
import shelve
import xbob.db.maskattack as db
from .. import spoof

def main():
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'database')
  LBP_DIR = os.path.join(basedir, 'lbp_features')
  CROPPED_DIR = os.path.join(basedir, 'img_cropped')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-id', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-ld', '--lbp-dir', dest="lbpdir", default=LBP_DIR, help="This path will be prepended to the LBP feature files output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-cd', '--cropped-dir', dest="croppeddir", default=CROPPED_DIR, help="This path will be prepended to the cropped color images output/used by this procedure (defaults to '%(default)s')")
  parser.add_argument('-n', '--normface-size', dest="normfacesize", default=64, type=int, help="this is the size of the normalized face box if face normalization is used (defaults to '%(default)s')")
  parser.add_argument('-l', '--lbptype', metavar='LBPTYPE', type=str, choices=('regular', 'riu2', 'uniform', 'maatta11'), default='uniform', dest='lbptype', help='Choose the type of LBP to use (defaults to "%(default)s")')
  parser.add_argument('-nl', dest='normlbp', action='store_true', default=True, help='If set to False, the the histograms will not be normalized.')
  parser.add_argument('--el', '--elbptype', metavar='ELBPTYPE', type=str, choices=('regular', 'transitional', 'direction_coded', 'modified'), default='regular', dest='elbptype', help='Choose the type of extended LBP features to compute (defaults to "%(default)s")')
  parser.add_argument('-b', '--blocks', metavar='BLOCKS', type=int, default=1, dest='blocks', help='The region over which the LBP is calculated will be divided into the given number of blocks squared. The histograms of the individial blocks will be concatenated.(defaults to "%(default)s")')
  parser.add_argument('-o', dest='overlap', action='store_true', default=False, help='If set, the blocks on which the image is divided will be overlapping')
  parser.add_argument('-sc', dest='skipcrop', action='store_true', default=False, help='If set, the cropping will be skipped and instead, previously generated cropped images will be used.')
  
  args = parser.parse_args()
  
  lbphistlength = {'regular':256, 'riu2':10, 'uniform':59, 'maatta11':833} # hardcoding the number of bins for the LBP variants
  
  # check if the given directories exist
  if not os.path.exists(args.lbpdir):
    bob.db.utils.makedirs_safe(args.lbpdir)
    
  if not os.path.exists(args.croppeddir):
    bob.db.utils.makedirs_safe(args.croppeddir)

  # query the database
  database = db.Database()
  allObjects = database.objects()
  
  # load registration data if the files are to be cropped
  if(not args.skipcrop):
    reg_file = os.path.join(args.inputdir,'documentation','registration.dat')
    f = shelve.open(reg_file)
    reg = f['reg_data']
    f.close()
  
  # process each video
  for obj in allObjects:
    file_name = str(os.path.join(args.lbpdir,obj.path+'_c.hdf5'))
    if not os.path.exists(file_name):
      print("Processing file %s " % (obj.path))
      hist_color = numpy.zeros(args.blocks * args.blocks * lbphistlength[args.lbptype]) # initialize the accumulated histogram for uniform LBP for color
      hist_depth = numpy.zeros(args.blocks * args.blocks * lbphistlength[args.lbptype]) # initialize the accumulated histogram for uniform LBP for depth
      if(args.skipcrop):
        color_image, depth_image = obj.load(args.croppeddir,iseye=False)
      else:
        data_folder = os.path.join(args.inputdir,'Data')
        sz = args.normfacesize
        color_image, depth_image, eye_pos = obj.load(data_folder)
        eye_pos = eye_pos.astype(numpy.double)
        face_eyes_norm = bob.ip.FaceEyesNorm(eyes_distance = sz/2, crop_height = sz, crop_width = sz, crop_eyecenter_offset_h = sz/4, crop_eyecenter_offset_w = sz/2)
        cropped_color = numpy.ndarray((sz, sz), dtype = numpy.float64)
        cropped_depth = numpy.ndarray((sz, sz), dtype = numpy.float64)
        cropped_color_all = numpy.ndarray((color_image.shape[0], 1, sz, sz), dtype = numpy.uint8)
        cropped_depth_all = numpy.ndarray((color_image.shape[0], 1 ,sz, sz), dtype = numpy.uint16)
      # process each frame
      for k in range(0, color_image.shape[0]):
        if(args.skipcrop):
          cropped_color = color_image[k,0,:,:]
          cropped_depth = depth_image[k,0,:,:]      
        else:   
          # crop color image
          frame = bob.ip.rgb_to_gray(color_image[k,:,:,:])
          face_eyes_norm(frame, cropped_color, re_y = eye_pos[k][1], re_x = eye_pos[k][0], le_y = eye_pos[k][3], le_x = eye_pos[k][2])
          cropped_color_all[k,0,:,:] = cropped_color
          
          # crop depth image after registering the eye positions
          frame = depth_image[k,0,:,:]
          eye_pos_d = numpy.zeros(4)
          for y in range(eye_pos[k][1].astype(numpy.int)-40,eye_pos[k][1].astype(numpy.int)):
            for x in range(eye_pos[k][0].astype(numpy.int),eye_pos[k][0].astype(numpy.int)+40):
              index = y*640+x
              metric_depth = reg['raw_to_mm_shift'][frame[y,x]]
              if metric_depth == 0:
                count = 0
                for i in range(-2,3):
                  for j in range(-2,3):
                    if(y+j in range(0,480) and x+i in range(0,640)):
                      md = reg['raw_to_mm_shift'][frame[y+j,x+i]]
                      metric_depth = metric_depth+md
                      if md>0:
                        count = count+1
                if count>0:
                  metric_depth = metric_depth/count
              if metric_depth > 10000:
                metric_depth = 10000
              nx = (reg['registration_table'][index][0]+reg['depth_to_rgb_shift'][metric_depth])/256
              ny = reg['registration_table'][index][1]
              if(nx==eye_pos[k][0] and ny==eye_pos[k][1]):
                eye_pos_d[0] = x
                eye_pos_d[1] = y
                break
          for y in range(eye_pos[k][3].astype(numpy.int)-50,eye_pos[k][3].astype(numpy.int)):
            for x in range(eye_pos[k][2].astype(numpy.int),eye_pos[k][2].astype(numpy.int)+30):
              index = y*640+x
              metric_depth = reg['raw_to_mm_shift'][frame[y,x]]
              if metric_depth == 0:
                count = 0
                for i in range(-2,3):
                  for j in range(-2,3):
                    if(y+j in range(0,480) and x+i in range(0,640)):
                      md = reg['raw_to_mm_shift'][frame[y+j,x+i]]
                      metric_depth = metric_depth+md
                      if md>0:
                        count = count+1
                if count>0:
                  metric_depth = metric_depth/count
              if metric_depth > 10000:
                metric_depth = 10000
              nx = (reg['registration_table'][index][0]+reg['depth_to_rgb_shift'][metric_depth])/256
              ny = reg['registration_table'][index][1]
              if(nx==eye_pos[k][2] and ny==eye_pos[k][3]):
                eye_pos_d[2] = x
                eye_pos_d[3] = y
                break
          if(sum(eye_pos_d)==0):
            print 'ERROR: Eyes couldn\'t be registered!!!'
          face_eyes_norm(frame, cropped_depth, re_y = eye_pos_d[1], re_x = eye_pos_d[0], le_y = eye_pos_d[3], le_x = eye_pos_d[2])
          cropped_depth_all[k,0,:,:] = cropped_depth
          # to save the depth map as an image after intensity normalization
          #cropped_depth[cropped_depth>cropped_depth.min()+35]=cropped_depth.min()+35
          #cropped_depth = ((cropped_depth.astype(numpy.float) -cropped_depth.min())/(cropped_depth.max()-cropped_depth.min())*255).astype(numpy.uint8)
          #bob.io.save(cropped_depth.astype('uint8'), '%02d_%02d_%02d_%02d.jpg' % (database.fileID_to_clientID(obj.id), database.fileID_to_session(obj.id), database.fileID_to_shot(obj.id), (k/30)+1))
        
        if(args.lbptype != 'maatta11'):
          hist_c, vf = spoof.lbphist_frame(cropped_color.astype(numpy.uint8), args.lbptype, args.elbptype, norm=args.normlbp, numbl=args.blocks,  overlap=args.overlap)
          hist_d, vf = spoof.lbphist_frame(cropped_depth.astype(numpy.uint8), args.lbptype, args.elbptype, norm=args.normlbp, numbl=args.blocks,  overlap=args.overlap)
        else:
          hist1_c, vf = spoof.lbphist_frame(color_image2, 'uniform', norm=args.normlbp, numbl=3,  overlap=True)
          hist2_c, vf = spoof.lbphist_frame(color_image2, 'uniform', norm=args.normlbp, radius=2, neighbors=8)
          hist3_c, vf = spoof.lbphist_frame(color_image2, 'uniform', norm=args.normlbp, circ=True, radius=2, neighbors=16)
          hist_c = numpy.concatenate((hist1_c,hist2_c,hist3_c))
          hist1_d, vf = spoof.lbphist_frame(depth_image2, 'uniform', norm=args.normlbp, numbl=3,  overlap=True)
          hist2_d, vf = spoof.lbphist_frame(depth_image2, 'uniform', norm=args.normlbp, radius=2, neighbors=8)
          hist3_d, vf = spoof.lbphist_frame(depth_image2, 'uniform', norm=args.normlbp, circ=True, radius=2, neighbors=16)
          hist_d = numpy.concatenate((hist1_d,hist2_d,hist3_d))      
        hist_color = hist_color + hist_c # accumulate the histograms of all the frames one by one
        hist_depth = hist_depth + hist_d # accumulate the histograms of all the frames one by one
      
      hist_color = hist_color / color_image.shape[0] # averaging over the number of valid frames
      hist_depth = hist_depth / depth_image.shape[0] # averaging over the number of valid frames
      
      # save the cropped images if necessary
      if(not args.skipcrop): 
        file_name = os.path.join(args.croppeddir,obj.path+'.hdf5')
        file_hdf5 = bob.io.HDF5File(str(file_name), "w")
        file_hdf5.set('Color_Data', cropped_color_all)
        file_hdf5.set('Depth_Data', cropped_depth_all)
        del file_hdf5
      
      # save the LBP features
      arr = numpy.array(hist_color, dtype='float64')
      bob.io.save(arr.reshape([1,arr.size]),str(os.path.join(args.lbpdir,obj.path+'_c.hdf5')))
      arr = numpy.array(hist_depth, dtype='float64')
      bob.io.save(arr.reshape([1,arr.size]),str(os.path.join(args.lbpdir,obj.path+'_d.hdf5')))
  
  return 0

if __name__ == "__main__":
  main()
