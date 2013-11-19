#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013

"""Runs the ICP algorithm on 3D data taking each mask in 3DMAD database separately as the test set, in leave-one-out manner.
"""

import os, sys
import argparse
import bob
import numpy
import xbob.db.maskattack
import matplotlib
import matplotlib.pyplot
import vtk
import vtk.util.numpy_support as VN
import matplotlib.delaunay as triang
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def create_full_dataset(indir, objects):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = []
  for obj in objects:
    for ind in range(1,11):
      hdf5 = bob.io.HDF5File(str(os.path.join(indir,obj.path+'_'+str(ind).zfill(2)+'.hdf5')))
      dataset.append(hdf5.read('Shape_Data'))
  return dataset

def points2model(shape):
  points = vtk.vtkPoints()
  triangle = vtk.vtkTriangle()
  triangles = vtk.vtkCellArray()
  polydata = vtk.vtkPolyData()
  
  for i in range(0,shape.shape[1],7):
    for j in range(0,shape.shape[2],7):
      if shape[2,j,i] != 0:
        p = points.InsertNextPoint(shape[0,j,i],shape[1,j,i],shape[2,j,i])
  pts = VN.vtk_to_numpy(points.GetData())
  cens,edg,tris,neig = triang.delaunay(pts[:,0],pts[:,1])
  for t in range(0,len(tris)):
    tr = triangle.GetPointIds().SetId(0,tris[t][0])
    tr = triangle.GetPointIds().SetId(1,tris[t][1])
    tr = triangle.GetPointIds().SetId(2,tris[t][2])
    tr = triangles.InsertNextCell(triangle)
  polydata.SetPoints(points)
  polydata.SetPolys(triangles)
  polydata.Modified()
  return polydata

def compare_models(polydata1,polydata2):
  icp = vtk.vtkIterativeClosestPointTransform()
  tpdf = vtk.vtkTransformPolyDataFilter()
  
  icp.SetSource(polydata2)
  icp.SetTarget(polydata1)
  icp.GetLandmarkTransform().SetModeToRigidBody()
  icp.SetMaximumNumberOfIterations(50)
  icp.StartByMatchingCentroidsOn()
  icp.Modified()
  icp.Update()
  tpdf.SetInput(polydata2)
  tpdf.SetTransform(icp)
  tpdf.Update()
  polydata2 = tpdf.GetOutput()
  
  dist = 0
  numPt = polydata1.GetNumberOfPoints()
  for pt in range(0,numPt):
    source_pt = polydata1.GetPoint(pt)
    id = polydata2.FindPoint(source_pt)
    target_pt = polydata2.GetPoint(id)
    d = numpy.array(source_pt)-numpy.array(target_pt)
    dist = dist + (d[0]**2+d[1]**2+d[2]**2)**0.5
  avgDist1 = dist/numPt
  dist = 0
  numPt = polydata2.GetNumberOfPoints()
  for pt in range(0,numPt):
    target_pt = polydata2.GetPoint(pt)
    id = polydata1.FindPoint(target_pt)
    source_pt = polydata1.GetPoint(id)
    d = numpy.array(source_pt)-numpy.array(target_pt)
    dist = dist + (d[0]**2+d[1]**2+d[2]**2)**0.5
  avgDist2 = dist/numPt
  avgDist = -1*min(avgDist1,avgDist2)
  return avgDist

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'output')
  OUTPUT_DIR = os.path.join(basedir, 'result')
  
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the grayscale or depth file folders to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--output-dir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every result file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')
  
  args = parser.parse_args()
  
  inputdir = os.path.join(args.inputdir,'accumulated')
  if not os.path.exists(inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  make_sure_path_exists(os.path.join(args.outputdir,'ICP_accumulated'))
  
  db = xbob.db.maskattack.Database()
  
  # run experiments for each mask
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    MASK_LIST = [int(sge_task_id)]
  else:
    MASK_LIST = range(1,18)
  
  for mask in MASK_LIST:
    id_list = range(1,18)
    id_list.remove(mask)
    train_list = id_list[0:8]
    dev_list = id_list[8:16]
    all_objects = db.objects()
    train = []
    dev_enrol = []
    dev_probe_real = []
    test_enrol = []
    test_probe_mask = []
    test_probe_real = []
    # Construct sets in leave-one-out manner
    for obj in all_objects:
      if obj.client_id in train_list and obj.session is not 3:
        train.append(obj)
      elif obj.client_id in dev_list:
        if obj.session is 1:
          dev_enrol.append(obj)
        elif obj.session is 2:
          dev_probe_real.append(obj)
      elif obj.client_id is mask:
        if obj.session is 1:
          test_enrol.append(obj)
        elif obj.session is 2:
          test_probe_real.append(obj)
        else:
          test_probe_mask.append(obj)
    
    file_name = os.path.join(args.outputdir,'ICP_accumulated',str(mask).zfill(2)+'.hdf5')
    if not os.path.exists(file_name):
      print 'Loading shape files for experiments for mask #%d..' %mask
      dev_enrol = create_full_dataset(inputdir,dev_enrol)
      dev_probe_real = create_full_dataset(inputdir,dev_probe_real)
      test_enrol = create_full_dataset(inputdir,test_enrol)
      test_probe_mask = create_full_dataset(inputdir,test_probe_mask)
      test_probe_real = create_full_dataset(inputdir,test_probe_real)
      
      print 'Matching and calculating scores..'
      dev_scores_real = numpy.zeros((len(dev_probe_real),len(dev_enrol)))
      dev_impostor = []
      dev_genuine = []
      for e in range(0,len(dev_enrol)):
        enrol = points2model(dev_enrol[e])
        for p in range(0,len(dev_probe_real)):
          probe = points2model(dev_probe_real[p])
          score = compare_models(enrol,probe)
          dev_scores_real[p,e] = score
          if p/50 == e/50:
            dev_genuine.append(score)
          else:
            dev_impostor.append(score)
      
      test_scores_real = numpy.zeros((len(test_probe_real),len(test_enrol)))
      test_genuine = []
      for e in range(0,len(test_enrol)):
        enrol = points2model(test_enrol[e])
        for p in range(0,len(test_probe_real)):
          probe = points2model(test_probe_real[p])
          score = compare_models(enrol,probe)
          test_scores_real[p,e] = score
          test_genuine.append(score)
      
      test_scores_mask = numpy.zeros((len(test_probe_mask),len(test_enrol)))
      test_mask = []
      for e in range(0,len(test_enrol)):
        enrol = points2model(test_enrol[e])
        for p in range(0,len(test_probe_mask)):
          probe = points2model(test_probe_mask[p])
          score = compare_models(enrol,probe)
          test_scores_mask[p,e] = score
          test_mask.append(score)
      
      print 'Saving results to %s..' %file_name
      file_hdf5 = bob.io.HDF5File(str(file_name), "w")
      file_hdf5.set('Dev_Scores_Real', dev_scores_real)
      file_hdf5.set('Dev_Genuine', dev_genuine)
      file_hdf5.set('Dev_Impostor', dev_impostor)
      file_hdf5.set('Test_Scores_Real', test_scores_real)
      file_hdf5.set('Test_Genuine', test_genuine)
      file_hdf5.set('Test_Scores_Mask', test_scores_mask)
      file_hdf5.set('Test_Mask', test_mask)
      del file_hdf5
    else:
      file_hdf5 = bob.io.HDF5File(str(file_name))
      dev_genuine = file_hdf5.read('Dev_Genuine').tolist()
      dev_impostor = file_hdf5.read('Dev_Impostor').tolist()
      test_genuine = file_hdf5.read('Test_Genuine').tolist()
      test_mask = file_hdf5.read('Test_Mask').tolist()
      del file_hdf5
    
    '''#To plot and save the score distributions (not in the paper):
    t_eer = bob.measure.eer_threshold(dev_impostor, dev_genuine)
    dev_far,dev_frr = bob.measure.farfrr(dev_impostor, dev_genuine, t_eer)
    sfar,test_frr = bob.measure.farfrr(test_mask, test_genuine, t_eer)
    
    file_name = os.path.join(args.outputdir,'ICP_accumulated',str(mask).zfill(2)+'.png')
    minscore = min(dev_genuine+dev_impostor+test_mask)
    maxscore = max(dev_genuine+dev_impostor+test_mask)
    scorebins = numpy.linspace(minscore,maxscore,100)
    fig = matplotlib.pyplot.figure()
    title =  'Score Distribution for Mask %d (EER:%.2f%%,SFAR:%.2f%%)' %(mask,dev_far*100,sfar*100)
    matplotlib.pyplot.title(title, fontsize=15)
    matplotlib.pyplot.xlabel('Score bins', fontsize=20)
    matplotlib.pyplot.ylabel('Number of Attempts', fontsize=20)
    p1 = matplotlib.pyplot.hist(dev_impostor, bins=scorebins, normed=True, alpha=0.4, color='r', label='Impostor Scores')
    p2 = matplotlib.pyplot.hist(dev_genuine, bins=scorebins, normed=True, alpha=0.4, color='g', label='Genuine Scores')
    p3 = matplotlib.pyplot.hist(test_mask, bins=scorebins, normed=True, alpha=0.4, color='b', label='Attack Scores')
    matplotlib.pyplot.vlines(t_eer, 0, max(p1[0]+p2[0]+p3[0]), linestyles='dashed',  label='EER Threshold')
    matplotlib.pyplot.legend(prop={'size':17})
    matplotlib.pyplot.grid()
    matplotlib.pyplot.savefig(file_name, bbox_inches='tight')'''
  
  return 0

if __name__ == "__main__":
  main()
