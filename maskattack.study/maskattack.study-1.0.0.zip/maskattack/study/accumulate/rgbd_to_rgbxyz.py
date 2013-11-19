import sys, os
import argparse
import shelve
import numpy
import bob
import random
import math
import errno

def findDepthCoord(x,y,reg,depth_img):
  diff = 100;
  for ny in range(y-50,y):
    for nx in range(x,x+30):
      index = ny*640+nx
      metric_depth = reg['raw_to_mm_shift'][depth_img[ny,nx]]
      if metric_depth == 0:
        count = 0
        for i in range(-2,3):
          for j in range(-2,3):
            if(ny+j in range(0,480) and nx+i in range(0,640)):
              md = reg['raw_to_mm_shift'][depth_img[ny+j,nx+i]]
              metric_depth = metric_depth+md
              if md>0:
                count = count+1
        if count>0:
          metric_depth = metric_depth/count
      if metric_depth > 10000:
        metric_depth = 10000
      nnx = (reg['registration_table'][index][0]+reg['depth_to_rgb_shift'][metric_depth])/256
      nny = reg['registration_table'][index][1]
      diff_new = abs(nnx-x)+abs(nny-y)
      if diff_new == 0:
        return nx,ny
      if diff_new < diff:
        diff = diff_new
        rx = nx
        ry = ny        
  return rx, ry

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'output/aligned')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-r', '--res', dest="resolution", default=128, type=int, help="Resolution of the final depth/color map (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')

  args = parser.parse_args()
  res = args.resolution
  outputdir = args.outputdir
  
  regfile = os.path.join(args.inputdir,'documentation/registration.dat')
  f = shelve.open(regfile)
  reg = f['reg_data']
  f.close()
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")  
  
  datadir = os.path.join(args.inputdir,'Data')
  if not os.path.exists(datadir):
    parser.error("Data directory does not exist")
  
  make_sure_path_exists(outputdir)
  
  hdf5_files = sorted([f for f in os.listdir(datadir) if f.endswith('.hdf5')])
  
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    FILE_LIST = [hdf5_files[int(sge_task_id)-1]]
  else:
    FILE_LIST = hdf5_files
  
  for f in FILE_LIST:
    file_path = os.path.join(outputdir,f)
    if(not os.path.exists(file_path)):
      print 'Reading the HDF5 file: %s' %f
      hdf5 = bob.io.HDF5File(os.path.join(datadir,f))
      depth = hdf5.read('Depth_Data')
      color = hdf5.read('Color_Data')
      eyes = hdf5.read('Eye_Pos')
      del hdf5
      XYZ = numpy.ones([300,3,res,res])*-9999
      RGB = numpy.zeros([300,3,res,res]).astype(numpy.uint8)
      for i in range(0,300): 
        sys.stdout.write('Processing frame: %d\r' % (i))
        sys.stdout.flush()
        depth_img = depth[i,0,:,:]
        color_img = color[i,:,:,:]
        eye_pos = eyes[i,:]
        eye_pos_d = numpy.zeros(4)
        color_img_d = numpy.zeros(color_img.shape)
        eye_pos_d[0], eye_pos_d[1] = findDepthCoord(eye_pos[0],eye_pos[1],reg,depth_img)
        eye_pos_d[2], eye_pos_d[3] = findDepthCoord(eye_pos[2],eye_pos[3],reg,depth_img)
        nx=depth_img[eye_pos_d[1]:eye_pos_d[1]+50,eye_pos_d[0]:eye_pos_d[2]].min(axis=0).argmin()
        ny=depth_img[eye_pos_d[1]:eye_pos_d[1]+50,eye_pos_d[0]:eye_pos_d[2]].argmin(axis=0)[nx]
        nx = eye_pos_d[0]+nx
        ny = eye_pos_d[1]+ny
        factor = 2*reg['zero_plane_info']['reference_pixel_size']/reg['zero_plane_info']['reference_distance']
        nzmm = reg['raw_to_mm_shift'][depth_img[ny,nx]]
        nxmm = (nx-320)*factor*nzmm
        nymm = (ny-240)*factor*nzmm
        for y in range(int(ny-res/2),int(ny+res/2)):
          for x in range(int(nx-res/2),int(nx+res/2)):
            zmm = reg['raw_to_mm_shift'][depth_img[y,x]]
            if zmm > 10000:
              zmm = 10000
            xmm = (x-320)*factor*zmm
            ymm = (y-240)*factor*zmm
            dist = math.sqrt(pow(nxmm-xmm,2)+pow(nymm-ymm,2)+pow(float(nzmm)-float(zmm),2))
            if(dist<80):
              index = y*640+x
              px = (reg['registration_table'][index][0]+reg['depth_to_rgb_shift'][zmm])/256
              py = reg['registration_table'][index][1]
              if(px in range(0,640) and py in range(0,480)):
                XYZ[i, :, y-(ny-res/2), x-(nx-res/2)] = [xmm, ymm, zmm]
                RGB[i, :, y-(ny-res/2), x-(nx-res/2)] = [color_img[0,py,px], color_img[1,py,px], color_img[2,py,px]]
      print "Saving the hdf5 file.."
      file_hdf5 = bob.io.HDF5File(file_path, 'w')
      file_hdf5.set('Shape_Data', XYZ, compression=9)
      file_hdf5.set('Color_Data', RGB, compression=9)
      del file_hdf5

  return 0

if __name__ == "__main__":
  main()
