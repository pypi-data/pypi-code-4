#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Runs the ISV algorithm on 2D or 2.5D images taking each mask in 3DMAD database separately as the test set, in leave-one-out manner.
"""

import os, sys
import argparse
import bob
import numpy
import xbob.db.maskattack
import matplotlib
import matplotlib.pyplot
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def create_full_dataset(indir, ftdir, objects, extractor, isarray=False):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = None
  for obj in objects:
    for ind in range(1,11):
      file_name = os.path.join(ftdir,obj.path+'_'+str(ind).zfill(2)+'.hdf5')
      try:
        file_hdf5 = bob.io.HDF5File(str(file_name))
        ft = file_hdf5.read('LBP_Feature')
      except:
        img = bob.io.load(str(os.path.join(indir,obj.path+'_'+str(ind).zfill(2)+'.png')))
        if len(img.shape)>2:
          img = bob.ip.rgb_to_gray(img)
        image2 = numpy.zeros((64,64))
        bob.ip.scale(numpy.array(img),image2)
        ft = extractor(image2)
        if not os.path.exists(file_name):
          try:
            file_hdf5 = bob.io.HDF5File(str(file_name), "w")
            file_hdf5.set('DCT_Feature', ft)
            del file_hdf5
          except:
            pass
      if isarray:
        if dataset is None:
          dataset = ft
        else:
          dataset = numpy.vstack((dataset, ft))
  return dataset

def ubm_project(ftdir,objects,ubm,client_num):
  array_proj = [[] for x in xrange(client_num)]
  ind = 0
  id_old = objects[0].client_id
  for obj in objects:
    for i in range(1,11):
      ft_file = os.path.join(ftdir,obj.path+'_'+str(i).zfill(2)+'.hdf5')
      if not os.path.exists(ft_file):
        raise IOError('Feature for file %s does not exist'%ft_file)
      else:
        file_hdf5 = bob.io.HDF5File(str(ft_file))
        ft = file_hdf5.read('DCT_Feature')
        gmm_stats = bob.machine.GMMStats(ubm.dim_c,ubm.dim_d)
        gmm_stats.init()
        ubm.acc_statistics(ft,gmm_stats)
        id_new = obj.client_id
        if(id_new is not id_old):
          ind = ind+1
          id_old = id_new
        array_proj[ind].append(gmm_stats)
  return array_proj

def isv_project(array,ubm,isvbase):
  array_proj = []
  for i in range(0,len(array)):
    list = []
    for j in range(0,len(array[0])):
      array_isv = numpy.ndarray(shape=(ubm.dim_c*ubm.dim_d,), dtype=numpy.float64)
      isv_machine = bob.machine.ISVMachine(isvbase)
      isv_machine.estimate_ux(array[i][j], array_isv)
      list.append(array_isv)
    array_proj.append(list)
  return array_proj      

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'output')
  FEATURE_DIR = os.path.join(basedir, 'feature')
  OUTPUT_DIR = os.path.join(basedir, 'result')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the grayscale or depth file folders to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-f', '--feature-dir', dest='featuredir', default=FEATURE_DIR, metavar='DIR', type=str, help='This path will be prepended to every feature file output by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--output-dir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every result file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-t', '--type', dest="type", default='grayscale', choices=('grayscale', 'depth'), help="Type of input images to be analyzed by this procedure (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')
  
  args = parser.parse_args()
  ftdir = os.path.join(FEATURE_DIR,'ISV',args.type)
  
  inputdir = os.path.join(args.inputdir,args.type)
  if not os.path.exists(inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  make_sure_path_exists(os.path.join(args.outputdir,'ISV_'+args.type))
  make_sure_path_exists(ftdir)
  
  db = xbob.db.maskattack.Database()
  dct_size = 45
 
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
         
    file_name = os.path.join(args.outputdir,'ISV_'+args.type,str(mask).zfill(2)+'.hdf5')
    if not os.path.exists(file_name):    
      print 'Extracting/loading DCT features for mask #%d..' %mask
      extractor = bob.ip.DCTFeatures(12,12,11,11,dct_size,True,True)
      train_dct = create_full_dataset(inputdir,ftdir,train,extractor,True)
      create_full_dataset(inputdir,ftdir,dev_enrol,extractor)
      create_full_dataset(inputdir,ftdir,dev_probe_real,extractor)
      create_full_dataset(inputdir,ftdir,test_enrol,extractor)
      create_full_dataset(inputdir,ftdir,test_probe_mask,extractor)
      create_full_dataset(inputdir,ftdir,test_probe_real,extractor)      
      print train_dct.shape, bob.version, train_dct[:,0], os.uname()[1]
      
      print 'Training k-means..'
      kmeans = bob.machine.KMeansMachine(512,dct_size-1)
      ubm = bob.machine.GMMMachine(512,dct_size-1)

      kmeans_trainer = bob.trainer.KMeansTrainer()
      kmeans_trainer.convergence_threshold = 5e-4
      kmeans_trainer.max_iterations = 500
      kmeans_trainer.train(kmeans,train_dct)
      
      [variances, weights] = kmeans.get_variances_and_weights_for_each_cluster(train_dct)
      means = kmeans.means

      ubm.means = means
      ubm.variances = variances
      ubm.weights = weights
      ubm.set_variance_thresholds(5e-4)
      
      print 'Training UBMGMM..'
      trainer = bob.trainer.ML_GMMTrainer(True,True,True,5e-4)
      trainer.convergence_threshold = 5e-4
      trainer.max_iterations = 500
      trainer.train(ubm,train_dct)
      
      print 'Projecting features (UBM)..'
      train_dct_ubm = ubm_project(ftdir,train,ubm,8)
      dev_enrol_dct_ubm = ubm_project(ftdir,dev_enrol,ubm,8)
      dev_probe_real_dct_ubm = ubm_project(ftdir,dev_probe_real,ubm,8)
      test_enrol_dct_ubm = ubm_project(ftdir,test_enrol,ubm,1)
      test_probe_mask_dct_ubm = ubm_project(ftdir,test_probe_mask,ubm,1)
      test_probe_real_dct_ubm = ubm_project(ftdir,test_probe_real,ubm,1)
            
      print 'Training ISV..'
      isvbase = bob.machine.ISVBase(ubm,160)
      isv_trainer = bob.trainer.ISVTrainer(10,4)
      isv_trainer.train(isvbase,train_dct_ubm)
      
      print 'Projecting features (ISV)..'
      dev_enrol_dct_ubm_isv = isv_project(dev_enrol_dct_ubm,ubm,isvbase)
      dev_probe_real_dct_ubm_isv = isv_project(dev_probe_real_dct_ubm,ubm,isvbase)
      test_enrol_dct_ubm_isv = isv_project(test_enrol_dct_ubm,ubm,isvbase)
      test_probe_mask_dct_ubm_isv = isv_project(test_probe_mask_dct_ubm,ubm,isvbase)
      test_probe_real_dct_ubm_isv = isv_project(test_probe_real_dct_ubm,ubm,isvbase)
      
      print 'Enrolling dev and test models..'
      dev_models = []
      for client_features in dev_enrol_dct_ubm:
        for enroll_feature in client_features:
          isv_machine = bob.machine.ISVMachine(isvbase)
          isv_trainer.enrol(isv_machine,[enroll_feature],1)
          dev_models.append(isv_machine)
      
      test_models = []
      for client_features in test_enrol_dct_ubm:
        for enroll_feature in client_features:
          isv_machine = bob.machine.ISVMachine(isvbase)
          isv_trainer.enrol(isv_machine,[enroll_feature],1)
          test_models.append(isv_machine)
      
      print 'Matching and calculating scores..'
      dev_scores_real = numpy.zeros((len(dev_probe_real_dct_ubm)*len(dev_probe_real_dct_ubm[0]),len(dev_models)))
      dev_impostor = []
      dev_genuine = []
      for c in range(0,len(dev_probe_real_dct_ubm)):
        for p in range(0,len(dev_probe_real_dct_ubm[0])):
          gmmstats = dev_probe_real_dct_ubm[c][p]
          Ux = dev_probe_real_dct_ubm_isv[c][p]
          for m in range(0,len(dev_models)):
            model = dev_models[m]
            score = model.forward_ux(gmmstats, Ux)
            dev_scores_real[c*len(dev_probe_real_dct_ubm[0])+p,m] = score
            if c == m/len(dev_probe_real_dct_ubm[0]):
              dev_genuine.append(score)
            else:
              dev_impostor.append(score)

      test_scores_real = numpy.zeros((len(test_probe_real_dct_ubm)*len(test_probe_real_dct_ubm[0]),len(test_models)))
      test_genuine = []
      for c in range(0,len(test_probe_real_dct_ubm)):
        for p in range(0,len(test_probe_real_dct_ubm[0])):
          gmmstats = test_probe_real_dct_ubm[c][p]
          Ux = test_probe_real_dct_ubm_isv[c][p]
          for m in range(0,len(test_models)):
            model = test_models[m]
            score = model.forward_ux(gmmstats, Ux)
            test_scores_real[c*len(test_probe_real_dct_ubm[0])+p,m] = score
            test_genuine.append(score)

      test_scores_mask = numpy.zeros((len(test_probe_mask_dct_ubm)*len(test_probe_mask_dct_ubm[0]),len(test_models)))
      test_mask = []
      for c in range(0,len(test_probe_mask_dct_ubm)):
        for p in range(0,len(test_probe_mask_dct_ubm[0])):
          gmmstats = test_probe_mask_dct_ubm[c][p]
          Ux = test_probe_mask_dct_ubm_isv[c][p]
          for m in range(0,len(test_models)):
            model = test_models[m]
            score = model.forward_ux(gmmstats, Ux)
            test_scores_mask[c*len(test_probe_mask_dct_ubm[0])+p,m] = score
            test_mask.append(score)

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
    
    '''#To plot and save the score distributions (not in the paper):
    t_eer = bob.measure.eer_threshold(dev_impostor, dev_genuine)
    dev_far,dev_frr = bob.measure.farfrr(dev_impostor, dev_genuine, t_eer)
    sfar,test_frr = bob.measure.farfrr(test_mask, test_genuine, t_eer)
    
    file_name = os.path.join(args.outputdir,'ISV_'+args.type,str(mask).zfill(2)+'.png')
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
