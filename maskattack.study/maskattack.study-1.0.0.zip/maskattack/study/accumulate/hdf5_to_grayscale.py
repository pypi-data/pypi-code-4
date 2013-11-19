import os, sys
import argparse
import numpy
import bob
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'output/grayscale')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  args = parser.parse_args()
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")  
  
  datadir = os.path.join(args.inputdir,'Data')
  if not os.path.exists(datadir):
    parser.error("Data directory does not exist")
  
  make_sure_path_exists(args.outputdir)
    
  hdf5_files = sorted([f for f in os.listdir(datadir) if f.endswith('.hdf5')])
  
  face_eyes_norm = bob.ip.FaceEyesNorm(eyes_distance = 65, crop_height = 128, crop_width = 128, crop_eyecenter_offset_h = 32, crop_eyecenter_offset_w = 63.5)
  cropped_image = numpy.ndarray( (128, 128), dtype = numpy.float64 )
  
  for f in hdf5_files:
    img_name = os.path.join(args.outputdir,f.split('.')[0]+'_01.png')
    if(not os.path.exists(img_name)):
      print 'Reading the HDF5 file: %s' %f
      hdf5 = bob.io.HDF5File(os.path.join(datadir,f))
      color = hdf5.read('Color_Data')
      eyes = hdf5.read('Eye_Pos')
      del hdf5
      for frame in range(0,300,30):
        img = color[frame,:,:,:]
        eye = eyes[frame,:].astype('float')
        face_eyes_norm(bob.ip.rgb_to_gray(img), cropped_image, re_y = eye[1], re_x = eye[0], le_y = eye[3], le_x = eye[2])
        file_name = os.path.join(args.outputdir,f.split('.')[0]+'_%s.png') %str(frame/30+1).zfill(2)
        bob.io.save(cropped_image.astype('uint8'), file_name)
  
  return 0

if __name__ == "__main__":
  main()
