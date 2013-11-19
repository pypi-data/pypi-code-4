#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Runs the TPS algorithm on 3D data taking each mask in 3DMAD database separately as the test set, in leave-one-out manner.
"""

import os, sys
import argparse
import bob
import numpy
import xbob.db.maskattack
import matplotlib
import pkg_resources
import matplotlib.pyplot
from ._tps import extractWP
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def create_full_dataset(indir, ftdir, objects, filename, pointArray):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = []
  for obj in objects:
    for ind in range(1,11):
      shape_file = str(os.path.join(indir,obj.path+'_'+str(ind).zfill(2)+'.hdf5'))
      feature_file = str(os.path.join(ftdir,obj.path+'_'+str(ind).zfill(2)+'.hdf5'))
      try:
        hdf5 = bob.io.HDF5File(str(feature_file))
        wp = hdf5.read('TPSWP_Feature')
      except:
        hdf5 = bob.io.HDF5File(shape_file)
        shape = hdf5.read('Shape_Data')
        del hdf5
        wp = extractWP(shape,filename,pointArray)
        if not os.path.exists(feature_file):
          try:
            hdf5 = bob.io.HDF5File(feature_file, "w")
            hdf5.set('TPSWP_Feature', wp)
            del hdf5
          except:
            pass
      if len(dataset)==0:
        dataset = wp
      else:
        dataset = numpy.hstack((dataset, wp))
  return dataset
  
def compare_wp(wp1,wp2):
  N = len(wp1)
  eucDist = numpy.zeros(N)
  cosDist = numpy.zeros(N)
  for i in range(0,N):
    eucDist[i] = numpy.linalg.norm(wp1[i]-wp2[i])
    norm1 = numpy.linalg.norm(wp1[i])
    norm2 = numpy.linalg.norm(wp2[i])
    cosDist[i] = 1-sum(wp1[i]*wp2[i])/(norm1*norm2)
  distance = sum(eucDist[20:N-20]+cosDist[20:N-20])/(N-40)
  return -1*distance  

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'output')
  FEATURE_DIR = os.path.join(basedir, 'feature')
  OUTPUT_DIR = os.path.join(basedir, 'result')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the grayscale or depth file folders to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-f', '--feature-dir', dest='featuredir', default=FEATURE_DIR, metavar='DIR', type=str, help='This path will be prepended to every feature file output by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--output-dir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every result file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')
  
  args = parser.parse_args()
  ftdir = os.path.join(FEATURE_DIR,'TPS','accumulated')
  
  inputdir = os.path.join(args.inputdir,'accumulated')
  if not os.path.exists(inputdir):
    parser.error("input directory does not exist")
  
  if not os.path.exists(args.outputdir):
    bob.db.utils.makedirs_safe(args.outputdir)
  if not os.path.exists(os.path.join(args.outputdir,'TPS_accumulated')):
    bob.db.utils.makedirs_safe(os.path.join(args.outputdir,'TPS_accumulated'))
  if not os.path.exists(ftdir):
    bob.db.utils.makedirs_safe(ftdir)
  
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
    
    file_name = os.path.join(args.outputdir,'TPS_accumulated',str(mask).zfill(2)+'.hdf5')
    if not os.path.exists(file_name):
      print 'Extracting/loading TPS warping parameters for mask #%d..' %mask
      filename = pkg_resources.resource_filename('maskattack','study/analyze/gen.obj')
      pointArray = numpy.loadtxt(pkg_resources.resource_filename('maskattack','study/analyze/gen_pts.txt'))
      dev_enrol = create_full_dataset(inputdir, ftdir, dev_enrol, filename, pointArray)
      dev_probe_real = create_full_dataset(inputdir, ftdir, dev_probe_real, filename, pointArray)
      test_enrol = create_full_dataset(inputdir, ftdir, test_enrol, filename, pointArray)
      test_probe_mask = create_full_dataset(inputdir, ftdir, test_probe_mask, filename, pointArray)
      test_probe_real = create_full_dataset(inputdir, ftdir, test_probe_real, filename, pointArray)
      
      print 'Matching and calculating scores..'
      dev_scores_real = numpy.zeros((dev_probe_real.shape[1]/3,dev_enrol.shape[1]/3))
      dev_impostor = []
      dev_genuine = []
      for e in range(0,dev_enrol.shape[1/3]):
        enrol = dev_enrol[:,3*e:3*e+3]
        for p in range(0,dev_probe_real.shape[1]/3):
          probe = dev_probe_real[:,3*p:3*p+3]
          score = compare_wp(enrol,probe)
          dev_scores_real[p,e] = score
          if p/50 == e/50:
            dev_genuine.append(score)
          else:
            dev_impostor.append(score)
    
      test_scores_real = numpy.zeros((test_probe_real.shape[1]/3,test_enrol.shape[1]/3))
      test_genuine = []
      for e in range(0,test_enrol.shape[1]/3):
        enrol = test_enrol[:,3*e:3*e+3]
        for p in range(0,test_probe_real.shape[1]/3):
          probe = test_probe_real[:,3*p:3*p+3]
          score = compare_wp(enrol,probe)
          test_scores_real[p,e] = score
          test_genuine.append(score)
      
      test_scores_mask = numpy.zeros((test_probe_mask.shape[1]/3,test_enrol.shape[1]/3))
      test_mask = []
      for e in range(0,test_enrol.shape[1]/3):
        enrol = test_enrol[:,3*e:3*e+3]
        for p in range(0,test_probe_mask.shape[1]/3):
          probe = test_probe_mask[:,3*p:3*p+3]
          score = compare_wp(enrol,probe)
          test_scores_mask[p,e] = score
          test_mask.append(score)  
      
      print 'Saving results id %s..' %file_name
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
    
    file_name = os.path.join(args.outputdir,'TPS_accumulated',str(mask).zfill(2)+'.png')
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
