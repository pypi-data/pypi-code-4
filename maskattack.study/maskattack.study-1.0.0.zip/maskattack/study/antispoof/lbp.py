#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Runs the LBP-based antispoofing algorithms on 2D or 2.5D images taking each mask in 3DMAD database separately as the test set, in leave-one-out manner.
"""

import os, sys
import argparse
import bob
import numpy
import xbob.db.maskattack
import matplotlib.pyplot
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def create_full_dataset(indir, ftdir, objects, lbp, blocks):
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
        ft = lbphist(image2,lbp,blocks)
        if not os.path.exists(file_name):
          try:
            file_hdf5 = bob.io.HDF5File(str(file_name), "w")
            file_hdf5.set('LBP_Feature', ft)
            del file_hdf5
          except:
            pass
      if dataset is None:
        dataset = ft
      else:
        dataset = numpy.vstack((dataset, ft))
  return dataset

def divideframe(frame,overlap=False):
  blockslist = [] 
  if overlap:
    start = [1,17,33]
    width = 30
  else:
    start = [0,21,42]
    width =  21
  for x in range(0,3):
    for y in range(0,3):
      sx = start[x]
      sy = start[y]
      nextblock = frame[sx:sx+width, sy:sy+width]
      blockslist.append(nextblock)
  return blockslist # list of subblocks as frames
  
def lbphist(img,lbptype,blocks):
  norm = False
  elbptype = {'regular':bob.ip.ELBPType.REGULAR, 'transitional':bob.ip.ELBPType.TRANSITIONAL, 'direction_coded':bob.ip.ELBPType.DIRECTION_CODED}
  finalhist = numpy.array([])
  if lbptype != 'maatta11':
    if lbptype != 'modified':
      lbp = bob.ip.LBP(8,1,1,uniform=True,elbp_type=elbptype[lbptype]) 
    else:
      lbp = bob.ip.LBP(8,1,1,uniform=True,to_average=True)
    lbpimage = numpy.ndarray(lbp.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes
    lbp(img, lbpimage) # calculating the lbp image
    if blocks:
      blockslist = divideframe(lbpimage) # divide the lbp image into 3x3 overlapping blocks
      for bl in blockslist:
        hist = bob.ip.histogram(bl, 0, lbp.max_label-1, lbp.max_label)
        if norm:
          hist = hist / sum(hist) # histogram normalization
        finalhist = numpy.append(finalhist, hist) # concatenate the subblocks' already normalized histograms
    else:
      finalhist =bob.ip.histogram(lbpimage, 0, lbp.max_label-1, lbp.max_label)
  else:
    hist1 = numpy.array([]) 
    lbp1 = bob.ip.LBP(8,1,1,uniform=True)
    lbpimage = numpy.ndarray(lbp1.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes
    lbp1(img, lbpimage) # calculating the lbp image
    blockslist = divideframe(lbpimage,True) # divide the lbp image into 3x3 overlapping blocks
    for bl in blockslist:
      hist = bob.ip.histogram(bl, 0, lbp1.max_label-1, lbp1.max_label)
      if norm:
        hist = hist / sum(hist) # histogram normalization
      hist1 = numpy.append(hist1, hist) # concatenate the subblocks' already normalized histograms     
    lbp2 = bob.ip.LBP(8,2,2,uniform=True,circular=True)
    lbpimage = numpy.ndarray(lbp2.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes  
    lbp2(img, lbpimage) # calculating the lbp image
    hist2 = bob.ip.histogram(lbpimage, 0, lbp2.max_label-1, lbp2.max_label)   
    lbp3 = bob.ip.LBP(16,2,2,uniform=True,circular=True)
    lbpimage = numpy.ndarray(lbp3.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes 
    lbp3(img, lbpimage) # calculating the lbp image
    hist3 = bob.ip.histogram(lbpimage, 0, lbp3.max_label-1, lbp3.max_label)
    finalhist = numpy.concatenate((hist1,hist2,hist3))        
  return finalhist.astype(numpy.float)
  
def chi_dist(test, real_model, mask_model):
  real_d = bob.math.chi_square(test, real_model)
  mask_d = bob.math.chi_square(test, mask_model)
  return mask_d-real_d

def svm_predict(svm_machine, data):
  labels = [svm_machine.predict_class_and_scores(x)[1][0] for x in data]
  return labels

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'output')
  FEATURE_DIR = os.path.join(basedir, 'feature','antispoof')
  OUTPUT_DIR = os.path.join(basedir, 'result','antispoof')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-f', '--feature-dir', dest='featuredir', default=FEATURE_DIR, metavar='DIR', type=str, help='This path will be prepended to every feature file output by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-t', '--type', dest="type", default='grayscale', type=str, choices=('grayscale', 'depth'), help="The data type to be processsed (defaults to '%(default)s')")
  parser.add_argument('-l', '--lbptype', dest='lbptype', default='regular', metavar='LBPTYPE', type=str, choices=('regular', 'transitional', 'direction_coded', 'modified', 'maatta11'), help='Choose the type of LBP to use (defaults to "%(default)s")')
  parser.add_argument('-b', '--blocks', dest='blocks', default=False, action='store_true', help='If set, the image will be divided into 3x3 overlapping blocks (except for LBP type maatta11 for which its own blocking method is always applied)')
  parser.add_argument('-c', '--classifier', dest='classifier', default='chi2', type=str, choices=('chi2', 'lda', 'svm'), help='Choose the type of LBP to use (defaults to "%(default)s")')
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')
  args = parser.parse_args()
  
  if args.blocks: bl = 'bl_'
  else: bl = ''
  
  indir = os.path.join(args.inputdir,args.type)
  ftdir = os.path.join(args.featuredir,args.type,bl+args.lbptype)
  outdir = os.path.join(args.outputdir,args.type)
  
  if not os.path.exists(indir):
    parser.error("input directory does not exist")

  make_sure_path_exists(outdir)
  make_sure_path_exists(ftdir)
      
  db = xbob.db.maskattack.Database()
  
  # run experiments for each mask
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    MASK_LIST = [int(sge_task_id)]
  else:
    MASK_LIST = range(1,18)
    
  DEV_REAL = []
  DEV_MASK = []
  TEST_REAL = []
  TEST_MASK = []
  DEER = []
  THTER = []
  AUC = []
  BEST = []
  for mask in MASK_LIST:
    id_list = range(1,18)
    id_list.remove(mask)
    train_list = id_list[0:8]
    dev_list = id_list[8:16]
    all_objects = db.objects()
    train_real = []
    train_mask = []
    dev_real = []
    dev_mask = []
    test_real = []
    test_mask = []
    for obj in all_objects:
      if obj.client_id in train_list:
        if obj.session is not 3:
          train_real.append(obj)
        else:
          train_mask.append(obj)
      elif obj.client_id in dev_list:
        if obj.session is not 3:
          dev_real.append(obj)
        else:
          dev_mask.append(obj)
      elif obj.client_id is mask:
        if obj.session is not 3:
          test_real.append(obj)
        else:
          test_mask.append(obj)
    
    print 'Extracting/loading LBP features for mask #%d..' %mask
    train_real_lbp = create_full_dataset(indir,ftdir,train_real,args.lbptype,args.blocks)
    train_mask_lbp = create_full_dataset(indir,ftdir,train_mask,args.lbptype,args.blocks)
    dev_real_lbp = create_full_dataset(indir,ftdir,dev_real,args.lbptype,args.blocks)
    dev_mask_lbp = create_full_dataset(indir,ftdir,dev_mask,args.lbptype,args.blocks)
    test_real_lbp = create_full_dataset(indir,ftdir,test_real,args.lbptype,args.blocks)
    test_mask_lbp = create_full_dataset(indir,ftdir,test_mask,args.lbptype,args.blocks)
    
    print 'Training for the %s classification method..' %args.classifier
    if args.classifier == 'chi2':
      print ".. Calculating real and mask models.."
      model_real = numpy.mean(train_real_lbp, axis=0) #average of the real train data lbp histograms
      model_mask = numpy.mean(train_mask_lbp, axis=0) #average of the mask train data lbp histograms
    elif args.classifier == 'lda':
      print ".. Running PCA reduction keeping 99% of the energy.."
      train_all = numpy.append(train_real_lbp, train_mask_lbp, axis=0)
      T = bob.trainer.PCATrainer()
      [pca_machine, eigvalues] = T.train(train_all)
      cumEnergy = numpy.array([sum(eigvalues[0:eigvalues.size-i]) / sum(eigvalues) for i in range(0, eigvalues.size+1)])
      numeigvalues = len(cumEnergy)-sum(cumEnergy>0.99)
      pca_machine.resize(pca_machine.shape[0], int(numeigvalues))
      train_real_pca = numpy.vstack([pca_machine(d) for d in train_real_lbp])
      train_mask_pca = numpy.vstack([pca_machine(d) for d in train_mask_lbp])
      print ".. Training LDA machine.."
      T = bob.trainer.FisherLDATrainer()
      [lda_machine, eigvalues] = T.train((train_real_pca, train_mask_pca)) 
      lda_machine.shape = (lda_machine.shape[0], 1) #only use first component!
    else:
      print ".. Training SVM machine.."
      svm_trainer = bob.trainer.SVMTrainer(kernel_type = bob.machine._machine.svm_kernel_type.LINEAR, gamma=1e-5)
      svm_trainer.probability = True
      svm_machine = svm_trainer.train([train_real_lbp, train_mask_lbp])
      
    print 'Calculating scores..'
    if args.classifier == 'chi2':
      dev_real_scores = numpy.vstack([chi_dist(d,model_real, model_mask) for d in dev_real_lbp])[:,0]
      dev_mask_scores = numpy.vstack([chi_dist(d,model_real, model_mask) for d in dev_mask_lbp])[:,0]
      test_real_scores = numpy.vstack([chi_dist(d,model_real, model_mask) for d in test_real_lbp])[:,0]
      test_mask_scores = numpy.vstack([chi_dist(d,model_real, model_mask) for d in test_mask_lbp])[:,0]
    elif args.classifier == 'lda':
      dev_real_pca = numpy.vstack([pca_machine(d) for d in dev_real_lbp])
      dev_mask_pca = numpy.vstack([pca_machine(d) for d in dev_mask_lbp])
      test_real_pca = numpy.vstack([pca_machine(d) for d in test_real_lbp])
      test_mask_pca = numpy.vstack([pca_machine(d) for d in test_mask_lbp])
      dev_real_scores = numpy.vstack([lda_machine(d) for d in dev_real_pca])[:,0]
      dev_mask_scores = numpy.vstack([lda_machine(d) for d in dev_mask_pca])[:,0]
      test_real_scores = numpy.vstack([lda_machine(d) for d in test_real_pca])[:,0]
      test_mask_scores = numpy.vstack([lda_machine(d) for d in test_mask_pca])[:,0]
    else:
      dev_real_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in dev_real_lbp])
      dev_mask_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in dev_mask_lbp])
      test_real_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in test_real_lbp])
      test_mask_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in test_mask_lbp])
    if numpy.mean(dev_real_scores) < numpy.mean(dev_mask_scores):
      dev_real_scores= dev_real_scores * -1
      dev_mask_scores= dev_mask_scores * -1
      test_real_scores= test_real_scores * -1
      test_mask_scores= test_mask_scores * -1
    DEV_REAL.append(dev_real_scores)
    DEV_MASK.append(dev_mask_scores)
    TEST_REAL.append(test_real_scores)
    TEST_MASK.append(test_mask_scores)
    
    print 'Computing performance..'
    thres = bob.measure.eer_threshold(dev_mask_scores, dev_real_scores)
    dev_far, dev_frr = bob.measure.farfrr(dev_mask_scores, dev_real_scores, thres)
    test_far, test_frr = bob.measure.farfrr(test_mask_scores, test_real_scores, thres)
    DEER.append(dev_far*100)
    THTER.append((test_far+test_frr)*50)
    
    roc = bob.measure.roc(test_mask_scores, test_real_scores,101)
    area = 0
    for i in range(0,100):
      d = abs(roc[0][i+1]-roc[0][i])
      area = area+(d*roc[1][i]+d*roc[1][i+1])/2
    area_all = abs(roc[0][0]-roc[0][-1])*abs(roc[1][0]-roc[1][-1])
    auc = 1.0-(area/area_all)
    AUC.append(auc)   
    
    min_score = min(numpy.append(test_mask_scores,test_real_scores))
    max_score = max(numpy.append(test_mask_scores,test_real_scores))
    step = (max_score-min_score)/1000
    best_perf = 0
    for thres in numpy.arange(min_score,max_score,step):
      test_far, test_frr = bob.measure.farfrr(test_mask_scores, test_real_scores, thres)
      perf = 1-(test_far*len(test_mask_scores)+test_frr*len(test_real_scores))/(len(test_mask_scores)+len(test_real_scores))
      if perf>best_perf:
        best_perf = perf
        best_thres = thres      
    BEST.append(best_perf)
        
    '''#To plot and save the score distributions (not in the paper):
    file_name = os.path.join(outdir,bl+args.lbptype+'_'+args.classifier+'.png')
    minscore = min([dev_mask_scores.min(),dev_real_scores.min(),test_mask_scores.min(),test_real_scores.min()])
    maxscore = max([dev_mask_scores.max(),dev_real_scores.max(),test_mask_scores.max(),test_real_scores.max()])
    scorebins = numpy.linspace(minscore,maxscore,100)
    fig = matplotlib.pyplot.figure()
    title =  'Score Distribution for Mask %d (Dev-EER:%.2f%%,Test-HTER:%.2f%%)' %(mask,dev_far*100,(test_far+test_frr)*50)
    matplotlib.pyplot.title(title, fontsize=15)
    matplotlib.pyplot.xlabel('Score bins', fontsize=20)
    matplotlib.pyplot.ylabel('Number of Attempts', fontsize=20)
    p1 = matplotlib.pyplot.hist(dev_mask_scores, bins=scorebins, normed=True, alpha=0.4, color='r', label='Dev Mask Scores')
    p2 = matplotlib.pyplot.hist(dev_real_scores, bins=scorebins, normed=True, alpha=0.4, color='g', label='Dev Real Scores')
    p1 = matplotlib.pyplot.hist(test_mask_scores, bins=scorebins, normed=True, alpha=0.7, color='r', label='Test Mask Scores')
    p2 = matplotlib.pyplot.hist(test_real_scores, bins=scorebins, normed=True, alpha=0.7, color='g', label='Test Real Scores')
    matplotlib.pyplot.vlines(thres, 0, max(p1[0]+p2[0]+p3[0]), linestyles='dashed',  label='EER Threshold')
    matplotlib.pyplot.legend(prop={'size':17})
    matplotlib.pyplot.grid()
    matplotlib.pyplot.savefig(file_name, bbox_inches='tight')'''
  
  file_name = os.path.join(outdir,bl+args.lbptype+'_'+args.classifier+'.hdf5')
  print 'Saving results to file %s..' %file_name
  file_hdf5 = bob.io.HDF5File(str(file_name), "w")
  file_hdf5.set('Dev_Mask_Scores', DEV_MASK)
  file_hdf5.set('Dev_Real_Scores', DEV_REAL)
  file_hdf5.set('Test_Mask_Scores', TEST_MASK)
  file_hdf5.set('Test_Real_Scores', TEST_REAL)
  file_hdf5.set('Dev_EER', DEER)
  file_hdf5.set('Test_HTER', THTER)
  file_hdf5.set('Area_Under_Curve', AUC)
  file_hdf5.set('Test_Best_Accuracy', BEST)
  del file_hdf5
    
  return 0

if __name__ == "__main__":
  main()
