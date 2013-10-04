#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Jan 19 15:56:55 CET 2012

"""This script calculates the chi2 difference between a model histogram and the data histograms, assigning scores to the data according to this. Firstly, the EER threshold on the development set is calculated. The, according to this EER, the FAR, FRR and HTER for the test and development set are calculated. The script outputs a text file with the performance results.
"""

import os, sys
import argparse
import bob
import numpy
import xbob.db.maskattack as db
from numpy import random

def create_full_dataset(indir, objects, ext):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = None
  for obj in objects:
    filename = str(os.path.join(indir,obj.path+ext+'.hdf5'))
    fvs = bob.io.load(filename)
    if dataset is None:
      dataset = fvs
    else:
      dataset = numpy.append(dataset, fvs, axis = 0)
  return dataset

def map_scores(indir, score_dir, objects, score_list):
  """Maps frame scores to frames of the objects. Writes the scores for each frame in a file, NaN for invalid frames

  Keyword parameters:

  indir: the directory with the files with valid frames

  score_dir: the directory where the score files are going to be written

  objects: list of objects

  score_list: list of scores for the given objects
  """
  num_scores = 0 # counter for how many valid frames have been processed so far in total of all the objects
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    vf = bob.io.load(filename)
    vf_indices = list(numpy.where(vf == 1)[0]) # indices of the valid frames of the object
    nvf_indices = list(numpy.where(vf == 0)[0]) # indices of the invalid frames of the object
    scores = numpy.ndarray((len(vf), 1), dtype='float64') 
    scores[vf_indices] = score_list[num_scores:num_scores + len(vf_indices)] # set the scores of the valid frames
    scores[nvf_indices] = numpy.NaN # set NaN for the scores of the invalid frames
    num_scores += len(vf_indices) # increase the nu,ber of valid scores that have been already maped
    obj.save(scores, score_dir, '.hdf5') # save the scores

def main():

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'lbp_features')
  OUTPUT_DIR = os.path.join(basedir, 'res')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the scores to be loaded')
  parser.add_argument('-d', '--output-dir', metavar='DIR', type=str, dest='outputdir', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')
  parser.add_argument('-s', '--score', dest='score', action='store_true', default=False, help='If set, the final classification scores of all the frames will be dumped in a file')

  from .. import spoof
  from ..spoof import chi2

  args = parser.parse_args()

  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")

  if not os.path.exists(args.outputdir): # if the output directory doesn't exist, create it
    bob.db.utils.makedirs_safe(args.outputdir)
    
  print "Output directory set to \"%s\"" % args.outputdir
  
  roc_acc_c = numpy.zeros([2,101])
  dev_eer_far_c = []
  dev_eer_frr_c = []
  test_eer_far_c = []
  test_eer_frr_c = []
  dev_hter_far_c = []
  dev_hter_frr_c = []
  test_hter_far_c = []
  test_hter_frr_c = []
  
  roc_acc_d = numpy.zeros([2,101])
  dev_eer_far_d = []
  dev_eer_frr_d = []
  test_eer_far_d = []
  test_eer_frr_d = []
  dev_hter_far_d = []
  dev_hter_frr_d = []
  test_hter_far_d = []
  test_hter_frr_d = []
  
  fold_num = 1000
  database = db.Database()
  random.seed(42)

  for f in range(0,fold_num):
    #print f
    #print "Loading input files..."
    # loading the input files    
    
    id_list = range(1,18)
    random.shuffle(id_list)
    train_list = id_list[0:7]
    dev_list = id_list[7:12]
    test_list = id_list[12:17]
    all_objects = database.objects()
    process_train_real = []
    process_train_mask = []
    process_dev_real = []
    process_dev_mask = []
    process_test_real = []
    process_test_mask = []
    for obj in all_objects:
      if obj.client_id in train_list:
        if obj.session is not 3:
          process_train_real.append(obj)
        else:
          process_train_mask.append(obj)
      elif obj.client_id in dev_list:
        if obj.session is not 3:
          process_dev_real.append(obj)
        else:
          process_dev_mask.append(obj)
      elif obj.client_id in test_list:
        if obj.session is not 3:
          process_test_real.append(obj)
        else:
          process_test_mask.append(obj)
    
    # create the full datasets from the file data
    dev_real_c = create_full_dataset(args.inputdir, process_dev_real, '_c')
    dev_mask_c = create_full_dataset(args.inputdir, process_dev_mask, '_c')
    test_real_c = create_full_dataset(args.inputdir, process_test_real, '_c')
    test_mask_c = create_full_dataset(args.inputdir, process_test_mask, '_c')
    train_real_c = create_full_dataset(args.inputdir, process_train_real, '_c')
    train_mask_c = create_full_dataset(args.inputdir, process_train_mask, '_c')
    
    dev_real_d = create_full_dataset(args.inputdir, process_dev_real, '_d')
    dev_mask_d = create_full_dataset(args.inputdir, process_dev_mask, '_d')
    test_real_d = create_full_dataset(args.inputdir, process_test_real, '_d')
    test_mask_d = create_full_dataset(args.inputdir, process_test_mask, '_d')
    train_real_d = create_full_dataset(args.inputdir, process_train_real, '_d')
    train_mask_d = create_full_dataset(args.inputdir, process_train_mask, '_d')
    
    #print "Loading the models..."
    # loading the histogram models
    #print "Calculating the real average model..."
    model_hist_real_c = numpy.mean(train_real_c, axis=0) #average of the real train data lbp histograms
    model_hist_real_d = numpy.mean(train_real_d, axis=0) #average of the real train data lbp histograms
    
    #print "Calculating the Chi-2 differences..."
    # calculating the comparison scores with chi2 distribution for each protocol subset   
    sc_dev_realmodel_c = chi2.cmphistbinschimod(model_hist_real_c, (dev_real_c, dev_mask_c))
    sc_test_realmodel_c = chi2.cmphistbinschimod(model_hist_real_c, (test_real_c, test_mask_c))
    sc_train_realmodel_c = chi2.cmphistbinschimod(model_hist_real_c, (train_real_c, train_mask_c))
    
    sc_dev_realmodel_d = chi2.cmphistbinschimod(model_hist_real_d, (dev_real_d, dev_mask_d))
    sc_test_realmodel_d = chi2.cmphistbinschimod(model_hist_real_d, (test_real_d, test_mask_d))
    sc_train_realmodel_d = chi2.cmphistbinschimod(model_hist_real_d, (train_real_d, train_mask_d))
    
    #print "Saving the results in a file"
    # It is expected that the positives always have larger scores. Therefore, it is necessary to "invert" the scores by multiplying them by -1 (the chi-square test gives smaller scores to the data from the similar distribution)
    sc_dev_realmodel_c = (sc_dev_realmodel_c[0] * -1, sc_dev_realmodel_c[1] * -1)
    sc_test_realmodel_c = (sc_test_realmodel_c[0] * -1, sc_test_realmodel_c[1] * -1)
    sc_train_realmodel_c = (sc_train_realmodel_c[0] * -1, sc_train_realmodel_c[1] * -1)
    
    sc_dev_realmodel_d = (sc_dev_realmodel_d[0] * -1, sc_dev_realmodel_d[1] * -1)
    sc_test_realmodel_d = (sc_test_realmodel_d[0] * -1, sc_test_realmodel_d[1] * -1)
    sc_train_realmodel_d = (sc_train_realmodel_d[0] * -1, sc_train_realmodel_d[1] * -1)
    
    if args.score: # save the scores in a file
      vf_dir_c = os.path.join(args.inputdir+'_c', 'validframes') # input directory with the files with valid frames
      score_dir_c = os.path.join(args.outputdir, 'scores') # output directory for the socre files
      map_scores(vf_dir_c, score_dir_c, process_dev_real_c, sc_dev_realmodel_c[0]) 
      map_scores(vf_dir_c, score_dir_c, process_dev_mask_c, sc_dev_realmodel_c[1])
      map_scores(vf_dir_c, score_dir_c, process_test_real_c, sc_test_realmodel_c[0])
      map_scores(vf_dir_c, score_dir_c, process_test_mask_c, sc_test_realmodel_c[1])
      map_scores(vf_dir_c, score_dir_c, process_train_real_c, sc_train_realmodel_c[0])
      map_scores(vf_dir_c, score_dir_c, process_train_mask_c, sc_train_realmodel_c[1])
      
      vf_dir_d = os.path.join(args.inputdir+'_d', 'validframes') # input directory with the files with valid frames
      score_dir_d = os.path.join(args.outputdir, 'scores') # output directory for the socre files
      map_scores(vf_dir_d, score_dir_d, process_dev_real_d, sc_dev_realmodel_d[0]) 
      map_scores(vf_dir_d, score_dir_d, process_dev_mask_d, sc_dev_realmodel_d[1])
      map_scores(vf_dir_d, score_dir_d, process_test_real_d, sc_test_realmodel_d[0])
      map_scores(vf_dir_d, score_dir_d, process_test_mask_d, sc_test_realmodel_d[1])
      map_scores(vf_dir_d, score_dir_d, process_train_real_d, sc_train_realmodel_d[0])
      map_scores(vf_dir_d, score_dir_d, process_train_mask_d, sc_train_realmodel_d[1])
    
    devel_attack_scores_c = sc_dev_realmodel_c[1][:,0]
    devel_real_scores_c = sc_dev_realmodel_c[0][:,0]
    test_attack_scores_c = sc_test_realmodel_c[1][:,0]
    test_real_scores_c = sc_test_realmodel_c[0][:,0]
    roc_acc_c = roc_acc_c + bob.measure.roc(test_attack_scores_c,test_real_scores_c,101)
    
    devel_attack_scores_d = sc_dev_realmodel_d[1][:,0]
    devel_real_scores_d = sc_dev_realmodel_d[0][:,0]
    test_attack_scores_d = sc_test_realmodel_d[1][:,0]
    test_real_scores_d = sc_test_realmodel_d[0][:,0]
    roc_acc_d = roc_acc_d + bob.measure.roc(test_attack_scores_d,test_real_scores_d,101)
    
    eer_thr = bob.measure.eer_threshold(devel_attack_scores_c,devel_real_scores_c)
    devel_far, devel_frr = bob.measure.farfrr(devel_attack_scores_c, devel_real_scores_c, eer_thr)
    test_far, test_frr = bob.measure.farfrr(test_attack_scores_c, test_real_scores_c, eer_thr)
    dev_eer_far_c.append(devel_far)
    dev_eer_frr_c.append(devel_frr)
    test_eer_far_c.append(test_far)
    test_eer_frr_c.append(test_frr)
    
    eer_thr = bob.measure.eer_threshold(devel_attack_scores_d,devel_real_scores_d)
    devel_far, devel_frr = bob.measure.farfrr(devel_attack_scores_d, devel_real_scores_d, eer_thr)
    test_far, test_frr = bob.measure.farfrr(test_attack_scores_d, test_real_scores_d, eer_thr)
    dev_eer_far_d.append(devel_far)
    dev_eer_frr_d.append(devel_frr)
    test_eer_far_d.append(test_far)
    test_eer_frr_d.append(test_frr)
    
    hter_thr = bob.measure.min_hter_threshold(devel_attack_scores_c,devel_real_scores_c)
    devel_far, devel_frr = bob.measure.farfrr(devel_attack_scores_c, devel_real_scores_c, hter_thr)
    test_far, test_frr = bob.measure.farfrr(test_attack_scores_c, test_real_scores_c, hter_thr)
    dev_hter_far_c.append(devel_far)
    dev_hter_frr_c.append(devel_frr)
    test_hter_far_c.append(test_far)
    test_hter_frr_c.append(test_frr)
    
    hter_thr = bob.measure.min_hter_threshold(devel_attack_scores_d,devel_real_scores_d)
    devel_far, devel_frr = bob.measure.farfrr(devel_attack_scores_d, devel_real_scores_d, hter_thr)
    test_far, test_frr = bob.measure.farfrr(test_attack_scores_d, test_real_scores_d, hter_thr)
    dev_hter_far_d.append(devel_far)
    dev_hter_frr_d.append(devel_frr)
    test_hter_far_d.append(test_far)
    test_hter_frr_d.append(test_frr)
  
  # writing results
  tbl = []
  tbl.append(" ")
  tbl.append(" MEAN")
  tbl.append(" At EER threshold for color: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(dev_eer_far_c)*100, int(round(numpy.mean(dev_eer_far_c)*len(dev_mask_c))), len(dev_mask_c), 
       numpy.mean(dev_eer_frr_c)*100, int(round(numpy.mean(dev_eer_frr_c)*len(dev_real_c))), len(dev_real_c),
       numpy.mean((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(test_eer_far_c)*100, int(round(numpy.mean(test_eer_far_c)*len(test_mask_c))), len(test_mask_c), 
       numpy.mean(test_eer_frr_c)*100, int(round(numpy.mean(test_eer_frr_c)*len(test_real_c))), len(test_real_c),
       numpy.mean((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100))
  
  tbl.append(" At HTER threshold for color: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(dev_hter_far_c)*100, int(round(numpy.mean(dev_hter_far_c)*len(dev_mask_c))), len(dev_mask_c), 
       numpy.mean(dev_hter_frr_c)*100, int(round(numpy.mean(dev_hter_frr_c)*len(dev_real_c))), len(dev_real_c),
       numpy.mean((numpy.array(dev_hter_far_c)+numpy.array(dev_hter_frr_c))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(test_hter_far_c)*100, int(round(numpy.mean(test_hter_far_c)*len(test_mask_c))), len(test_mask_c), 
       numpy.mean(test_hter_frr_c)*100, int(round(numpy.mean(test_hter_frr_c)*len(test_real_c))), len(test_real_c),
       numpy.mean((numpy.array(test_hter_far_c)+numpy.array(test_hter_frr_c))/2)*100))
  
  tbl.append(" At EER threshold for depth: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(dev_eer_far_d)*100, int(round(numpy.mean(dev_eer_far_d)*len(dev_mask_d))), len(dev_mask_d), 
       numpy.mean(dev_eer_frr_d)*100, int(round(numpy.mean(dev_eer_frr_d)*len(dev_real_d))), len(dev_real_d),
       numpy.mean((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(test_eer_far_d)*100, int(round(numpy.mean(test_eer_far_d)*len(test_mask_d))), len(test_mask_d), 
       numpy.mean(test_eer_frr_d)*100, int(round(numpy.mean(test_eer_frr_d)*len(test_real_d))), len(test_real_d),
       numpy.mean((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100))
  
  tbl.append(" At HTER threshold for depth: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(dev_hter_far_d)*100, int(round(numpy.mean(dev_hter_far_d)*len(dev_mask_d))), len(dev_mask_d), 
       numpy.mean(dev_hter_frr_d)*100, int(round(numpy.mean(dev_hter_frr_d)*len(dev_real_d))), len(dev_real_d),
       numpy.mean((numpy.array(dev_hter_far_d)+numpy.array(dev_hter_frr_d))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.mean(test_hter_far_d)*100, int(round(numpy.mean(test_hter_far_d)*len(test_mask_d))), len(test_mask_d), 
       numpy.mean(test_hter_frr_d)*100, int(round(numpy.mean(test_hter_frr_d)*len(test_real_d))), len(test_real_d),
       numpy.mean((numpy.array(test_hter_far_d)+numpy.array(test_hter_frr_d))/2)*100))
  
  tbl.append(" ")
  tbl.append(" STD")
  tbl.append(" At EER threshold for color: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(dev_eer_far_c)*100, int(round(numpy.std(dev_eer_far_c)*len(dev_mask_c))), len(dev_mask_c), 
       numpy.std(dev_eer_frr_c)*100, int(round(numpy.std(dev_eer_frr_c)*len(dev_real_c))), len(dev_real_c),
       numpy.std((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(test_eer_far_c)*100, int(round(numpy.std(test_eer_far_c)*len(test_mask_c))), len(test_mask_c), 
       numpy.std(test_eer_frr_c)*100, int(round(numpy.std(test_eer_frr_c)*len(test_real_c))), len(test_real_c),
       numpy.std((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100))
  
  tbl.append(" At HTER threshold for color: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(dev_hter_far_c)*100, int(round(numpy.std(dev_hter_far_c)*len(dev_mask_c))), len(dev_mask_c), 
       numpy.std(dev_hter_frr_c)*100, int(round(numpy.std(dev_hter_frr_c)*len(dev_real_c))), len(dev_real_c),
       numpy.std((numpy.array(dev_hter_far_c)+numpy.array(dev_hter_frr_c))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(test_hter_far_c)*100, int(round(numpy.std(test_hter_far_c)*len(test_mask_c))), len(test_mask_c), 
       numpy.std(test_hter_frr_c)*100, int(round(numpy.std(test_hter_frr_c)*len(test_real_c))), len(test_real_c),
       numpy.std((numpy.array(test_hter_far_c)+numpy.array(test_hter_frr_c))/2)*100))
  
  tbl.append(" At EER threshold for depth: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(dev_eer_far_d)*100, int(round(numpy.std(dev_eer_far_d)*len(dev_mask_d))), len(dev_mask_d), 
       numpy.std(dev_eer_frr_d)*100, int(round(numpy.std(dev_eer_frr_d)*len(dev_real_d))), len(dev_real_d),
       numpy.std((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(test_eer_far_d)*100, int(round(numpy.std(test_eer_far_d)*len(test_mask_d))), len(test_mask_d), 
       numpy.std(test_eer_frr_d)*100, int(round(numpy.std(test_eer_frr_d)*len(test_real_d))), len(test_real_d),
       numpy.std((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100))
  
  tbl.append(" At HTER threshold for depth: ")
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(dev_hter_far_d)*100, int(round(numpy.std(dev_hter_far_d)*len(dev_mask_d))), len(dev_mask_d), 
       numpy.std(dev_hter_frr_d)*100, int(round(numpy.std(dev_hter_frr_d)*len(dev_real_d))), len(dev_real_d),
       numpy.std((numpy.array(dev_hter_far_d)+numpy.array(dev_hter_frr_d))/2)*100))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (numpy.std(test_hter_far_d)*100, int(round(numpy.std(test_hter_far_d)*len(test_mask_d))), len(test_mask_d), 
       numpy.std(test_hter_frr_d)*100, int(round(numpy.std(test_hter_frr_d)*len(test_real_d))), len(test_real_d),
       numpy.std((numpy.array(test_hter_far_d)+numpy.array(test_hter_frr_d))/2)*100))
  
  txt = ''.join([k+'\n' for k in tbl])
  tf = open(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_results.txt'), 'w')
  tf.write(txt)
  tf.close()
  
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_eer_c'), (numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_hter_c'), (numpy.array(test_hter_far_c)+numpy.array(test_hter_frr_c))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_eer_d'), (numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_hter_d'), (numpy.array(test_hter_far_d)+numpy.array(test_hter_frr_d))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_roc_c'), roc_acc_c/fold_num*100)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_roc_d'), roc_acc_d/fold_num*100)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_cmp_values'), [[numpy.mean((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100, numpy.mean((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100, numpy.mean((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100, numpy.mean((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100],[numpy.std((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100, numpy.std((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100, numpy.std((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100, numpy.std((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100]])

if __name__ == '__main__':
  main()
