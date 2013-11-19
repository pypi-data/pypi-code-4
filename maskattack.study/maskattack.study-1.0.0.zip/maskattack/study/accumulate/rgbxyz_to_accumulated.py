import os, sys
import argparse
import numpy
import bob
import vtk
import vtk.util.numpy_support as VN
import cv2
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'output/aligned')
  OUTPUT_DIR = os.path.join(basedir, 'output/accumulated')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-r', '--res', dest="resolution", default=300, type=int, help="Resolution of the final depth/color map (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')

  args = parser.parse_args()
  res = args.resolution
  outputdir = args.outputdir  
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(outputdir)
  
  hdf5_files = sorted([f for f in os.listdir(args.inputdir) if f.endswith('.hdf5')])
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    FILE_LIST = [hdf5_files[int(sge_task_id)-1]]
  else:
    FILE_LIST = hdf5_files
  
  for f in FILE_LIST:
    targetpoly = None
    for c in range(1,11):
      file_name = os.path.join(outputdir,f.split('.')[0]+'_%s.hdf5') %str(c).zfill(2)
      if(not os.path.exists(file_name)):
        print 'Reading the HDF5 file: %s' %f
        hdf5 = bob.io.HDF5File(os.path.join(args.inputdir,f))
        shape = hdf5.read('Shape_Data')
        color = hdf5.read('Color_Data')
        del hdf5
        print 'Accumulating each frame...'
        sumMap = numpy.zeros([res,res])
        sumRGB = numpy.zeros([3,res,res])
        counter = numpy.zeros([res,res])
        for frame in range((c-1)*30,300):
          sys.stdout.write('Processing frame: %d for model: %d\r' % (frame, frame/30+1))
          sys.stdout.flush()
          points = vtk.vtkPoints()
          sourcepoly = vtk.vtkPolyData()
          vxft = vtk.vtkVertexGlyphFilter()
          icp = vtk.vtkIterativeClosestPointTransform()
          tpdf = vtk.vtkTransformPolyDataFilter()
          clpd = vtk.vtkCleanPolyData()
          
          #Setting the first frame as the target model if needed
          if targetpoly is None:
            targetpoly = vtk.vtkPolyData()
            shape_img = shape[0,:,:,:]
            color_img = color[0,:,:,:]
            rgb = []
            for y in range(0,128):
              for x in range(0,128):
                if(shape_img[0,y,x] != -9999):
                  N = points.InsertNextPoint(shape_img[:,y,x])
                  rgb.append(color_img[:,y,x])
            rgb = numpy.array(rgb)    
            nxmm = shape_img[0,64,64]
            nymm = shape_img[1,64,64]      
            linx = numpy.linspace(nxmm-75,nxmm+75,res)
            liny = numpy.linspace(nymm-75,nymm+75,res)
            targetpoly.SetPoints(points)
            vxft.SetInputConnection(targetpoly.GetProducerPort())
            vxft.Update()
            targetpoly = vxft.GetOutput()
          
          #Setting the frame to be processed as the source model to be aligned (skip if it is the first frame)
          if frame != 0:
            shape_img = shape[frame,:,:,:]
            color_img = color[frame,:,:,:]
            rgb = []
            for y in range(0,128):
              for x in range(0,128):
                if(shape_img[0,y,x] != -9999):
                  N = points.InsertNextPoint(shape_img[:,y,x])
                  rgb.append(color_img[:,y,x])
            rgb = numpy.array(rgb)
            
            sourcepoly.SetPoints(points)
            vxft.SetInputConnection(sourcepoly.GetProducerPort())
            vxft.Update()
            sourcepoly = vxft.GetOutput()
            
            #Applying ICP alignment
            icp.SetSource(sourcepoly)
            icp.SetTarget(targetpoly)
            icp.GetLandmarkTransform().SetModeToRigidBody()
            icp.SetMaximumNumberOfIterations(50)
            icp.StartByMatchingCentroidsOn()
            icp.Modified()
            icp.Update()
            tpdf.SetInput(sourcepoly)
            tpdf.SetTransform(icp)
            tpdf.Update()
            sourcepoly = tpdf.GetOutput()
          else:
            sourcepoly = targetpoly
          
          #Remeshing and adding the frame...
          pts = VN.vtk_to_numpy(sourcepoly.GetPoints().GetData())
          for ind in range(0,len(pts)):
            i = numpy.abs(linx-pts[ind,0]).argmin()
            j = numpy.abs(liny-pts[ind,1]).argmin()
            sumMap[j,i] = sumMap[j,i]+pts[ind,2]
            sumRGB[0,j,i] = sumRGB[0,j,i]+rgb[ind,0]
            sumRGB[1,j,i] = sumRGB[1,j,i]+rgb[ind,1]
            sumRGB[2,j,i] = sumRGB[2,j,i]+rgb[ind,2]
            counter[j,i] = counter[j,i]+1
          
          if(frame%30==29):
            file_name = os.path.join(outputdir,f.split('.')[0]+'_%s.hdf5') %str(frame/30+1).zfill(2)
            avgMap = sumMap/counter
            avgRGB = sumRGB/[counter,counter,counter]
            cnt = 1
            while cnt>0:
              cnt = 0
              for i in range(2,res-2):
                for j in range(2,res-2):
                  block = avgMap[i-2:i+3,j-2:j+3]
                  if(numpy.isnan(avgMap[i,j]) and (sum(sum(numpy.isnan(block))))<12):
                    cnt = cnt+1
                    blockR = avgRGB[0,i-2:i+3,j-2:j+3]
                    blockG = avgRGB[1,i-2:i+3,j-2:j+3]
                    blockB = avgRGB[2,i-2:i+3,j-2:j+3]
                    avgRGB[0,i,j] = blockR[numpy.invert(numpy.isnan(block))].mean()
                    avgRGB[1,i,j] = blockG[numpy.invert(numpy.isnan(block))].mean()
                    avgRGB[2,i,j] = blockB[numpy.invert(numpy.isnan(block))].mean()
                    avgMap[i,j] = block[numpy.invert(numpy.isnan(block))].mean()
            validity = numpy.invert(numpy.isnan(avgMap))
            cnt = 1800
            while cnt>0:
              avgMap2 = numpy.array([row[:] for row in avgMap])
              cnt = 0
              for i in range(2,res-2):
                for j in range(2,res-2):
                  block = avgMap2[i-2:i+3,j-2:j+3]
                  if(numpy.isnan(avgMap[i,j])):
                    cnt = cnt+1
                    blockR = avgRGB[0,i-2:i+3,j-2:j+3]
                    blockG = avgRGB[1,i-2:i+3,j-2:j+3]
                    blockB = avgRGB[2,i-2:i+3,j-2:j+3]
                    avgRGB[0,i,j] = blockR[numpy.invert(numpy.isnan(block))].mean()
                    avgRGB[1,i,j] = blockG[numpy.invert(numpy.isnan(block))].mean()
                    avgRGB[2,i,j] = blockB[numpy.invert(numpy.isnan(block))].mean()
                    avgMap[i,j] = block[numpy.invert(numpy.isnan(block))].mean()
            avgMap[numpy.isnan(avgMap)] = 0
            avgRGB[numpy.isnan(avgRGB)] = 0
            avgMap = cv2.bilateralFilter(avgMap.astype(numpy.float32),10,50,50)
            avgMap = cv2.bilateralFilter(avgMap.astype(numpy.float32),10,50,50)
            avgRGB = cv2.bilateralFilter(avgRGB.transpose().swapaxes(0,1).astype(numpy.float32),10,50,50)
            avgRGB = cv2.bilateralFilter(avgRGB,5,10,10)
            avgRGB = avgRGB.swapaxes(0,1).transpose()*validity
            
            avgXYZ = numpy.zeros((3,res,res))
            avgXYZ[0:2,:] = numpy.meshgrid(linx,liny)
            avgXYZ[2,:] = avgMap*validity
           
            print "Saving the hdf5 file #%s.." %str(frame/30+1).zfill(2)
            file_hdf5 = bob.io.HDF5File(file_name, 'w')
            file_hdf5.set('Shape_Data', avgXYZ)
            file_hdf5.set('Color_Data', avgRGB)
            del file_hdf5
            
            sumMap = numpy.zeros([res,res])
            sumRGB = numpy.zeros([3,res,res])
            counter = numpy.zeros([res,res])
  
  return 0

if __name__ == "__main__":
  main()
