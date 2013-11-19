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
  INPUT_DIR = os.path.join(basedir, 'output/accumulated')
  OUTPUT_DIR = os.path.join(basedir, 'output/depth')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  args = parser.parse_args()
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  
  hdf5_files = sorted([f for f in os.listdir(args.inputdir) if f.endswith('.hdf5')])
  
  for f in hdf5_files:
    img_name = os.path.join(args.outputdir,f.split('.')[0]+'.png')
    if(not os.path.exists(img_name)):
      hdf5 = bob.io.HDF5File(os.path.join(args.inputdir,f))
      shape = hdf5.read('Shape_Data')
      a = shape[2,:,:].astype(numpy.uint16)
      a_zero = a==0
      a = a-a.max()+1000
      a[a_zero] = 1000
      bob.io.save(a.astype(numpy.uint16),img_name)
  
  return 0

if __name__ == "__main__":
  main()
