#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Feb  9 14:52:09 CET 2012

"""This script makes an LDA classification of data into two categories: real accesses and spoofing attacks. There is an option for normalizing and dimensionality reduction of the data prior to the LDA classification.
After the LDA, each data sample gets a score. Firstly, the EER threshold on the development set is calculated. The, according to this EER, the FAR, FRR and HTER for the test and development set are calculated. The script outputs a text file with the performance results.
The details about the procedure are described in the paper: "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing" - Chingovska, Anjos & Marcel; BIOSIG 2012
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
  return dataset[~numpy.isnan(dataset).any(axis=1)]  # remove all the Nan elements 

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

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the scores to be loaded')
  parser.add_argument('-d', '--output-dir', metavar='DIR', type=str, dest='outputdir', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')
  parser.add_argument('-n', '--normalize', action='store_true', dest='normalize', default=False, help='If True, will do zero mean unit variance normalization on the data before creating the LDA machine')
  parser.add_argument('-r', '--pca_reduction', action='store_true', dest='pca_reduction', default=False, help='If set, PCA dimensionality reduction will be performed to the data before doing LDA')
  parser.add_argument('-e', '--energy', type=str, dest="energy", default='0.99', help='The energy which needs to be preserved after the dimensionality reduction if PCA is performed prior to LDA')
  parser.add_argument('-s', '--score', dest='score', action='store_true', default=False, help='If set, the final classification scores of all the frames will be dumped in a file')

  from .. import ml
  from ..ml import pca, lda, norm

  args = parser.parse_args()

  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")

  if not os.path.exists(args.outputdir): # if the output directory doesn't exist, create it
    bob.db.utils.makedirs_safe(args.outputdir)

  energy = float(args.energy)
  
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
  
  for f in range(0,fold_num):
    #print f
    #print "Loading input files..."  
    
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
    
    if args.normalize:  # zero mean unit variance data normalziation
      #print "Applying standard normalization..."
      mean, std = norm.calc_mean_std(train_real_c, train_mask_c)
      train_real_c = norm.zeromean_unitvar_norm(train_real_c, mean, std); train_mask_c = norm.zeromean_unitvar_norm(train_mask_c, mean, std)
      dev_real_c = norm.zeromean_unitvar_norm(dev_real_c, mean, std); dev_mask_c = norm.zeromean_unitvar_norm(dev_mask_c, mean, std)
      test_real_c = norm.zeromean_unitvar_norm(test_real_c, mean, std); test_mask_c = norm.zeromean_unitvar_norm(test_mask_c, mean, std)
      
      mean, std = norm.calc_mean_std(train_real_d, train_mask_d)
      train_real_d = norm.zeromean_unitvar_norm(train_real_d, mean, std); train_mask_d = norm.zeromean_unitvar_norm(train_mask_d, mean, std)
      dev_real_d = norm.zeromean_unitvar_norm(dev_real_d, mean, std); dev_mask_d = norm.zeromean_unitvar_norm(dev_mask_d, mean, std)
      test_real_d = norm.zeromean_unitvar_norm(test_real_d, mean, std); test_mask_d = norm.zeromean_unitvar_norm(test_mask_d, mean, std)

    if args.pca_reduction: # PCA dimensionality reduction of the data
      #print "Running PCA reduction..."
      train_c = numpy.append(train_real_c, train_mask_c, axis=0)
      pca_machine_c = pca.make_pca(train_c, energy) # performing PCA
      train_real_c = pca.pcareduce(pca_machine_c, train_real_c); train_mask_c = pca.pcareduce(pca_machine_c, train_mask_c)
      dev_real_c = pca.pcareduce(pca_machine_c, dev_real_c); dev_mask_c = pca.pcareduce(pca_machine_c, dev_mask_c)
      test_real_c = pca.pcareduce(pca_machine_c, test_real_c); test_mask_c = pca.pcareduce(pca_machine_c, test_mask_c)
      
      train_d = numpy.append(train_real_d, train_mask_d, axis=0)
      pca_machine_d = pca.make_pca(train_d, energy) # performing PCA
      train_real_d = pca.pcareduce(pca_machine_d, train_real_d); train_mask_d = pca.pcareduce(pca_machine_d, train_mask_d)
      dev_real_d = pca.pcareduce(pca_machine_d, dev_real_d); dev_mask_d = pca.pcareduce(pca_machine_d, dev_mask_d)
      test_real_d = pca.pcareduce(pca_machine_d, test_real_d); test_mask_d = pca.pcareduce(pca_machine_d, test_mask_d)

    #print "Training LDA machine..."
    lda_machine_c = lda.make_lda((train_real_c, train_mask_c)) # training the LDA    
    lda_machine_c.shape = (lda_machine_c.shape[0], 1) #only use first component!

    lda_machine_d = lda.make_lda((train_real_d, train_mask_d)) # training the LDA
    lda_machine_d.shape = (lda_machine_d.shape[0], 1) #only use first component!

    #print "Computing dev and test scores..."
    dev_real_out_c = lda.get_scores(lda_machine_c, dev_real_c)
    dev_mask_out_c = lda.get_scores(lda_machine_c, dev_mask_c)
    test_real_out_c = lda.get_scores(lda_machine_c, test_real_c)
    test_mask_out_c = lda.get_scores(lda_machine_c, test_mask_c)
    train_real_out_c = lda.get_scores(lda_machine_c, train_real_c)
    train_mask_out_c = lda.get_scores(lda_machine_c, train_mask_c)
    
    dev_real_out_d = lda.get_scores(lda_machine_d, dev_real_d)
    dev_mask_out_d = lda.get_scores(lda_machine_d, dev_mask_d)
    test_real_out_d = lda.get_scores(lda_machine_d, test_real_d)
    test_mask_out_d = lda.get_scores(lda_machine_d, test_mask_d)
    train_real_out_d = lda.get_scores(lda_machine_d, train_real_d)
    train_mask_out_d = lda.get_scores(lda_machine_d, train_mask_d)

    # it is expected that the scores of the real accesses are always higher then the scores of the attacks. Therefore, a check is first made, if the average of the scores of real accesses is smaller then the average of the scores of the attacks, all the scores are inverted by multiplying with -1.
    if numpy.mean(dev_real_out_c) < numpy.mean(dev_mask_out_c):
      dev_real_out_c = dev_real_out_c * -1; dev_mask_out_c = dev_mask_out_c * -1
      test_real_out_c = test_real_out_c * -1; test_mask_out_c = test_mask_out_c * -1
      train_real_out_c = train_real_out_c * -1; train_mask_out_c = train_mask_out_c * -1   
    if numpy.mean(dev_real_out_d) < numpy.mean(dev_mask_out_d):
      dev_real_out_d = dev_real_out_d * -1; dev_mask_out_d = dev_mask_out_d * -1
      test_real_out_d = test_real_out_d * -1; test_mask_out_d = test_mask_out_d * -1
      train_real_out_d = train_real_out_d * -1; train_mask_out_d = train_mask_out_d * -1  

    if args.score: # save the scores in a file
      vf_dir_c = os.path.join(args.inputdir+'_c', 'validframes') # input directory with the files with valid frames
      score_dir_c = os.path.join(args.outputdir, 'scores') # output directory for the socre files
      map_scores(vf_dir_c, score_dir_c, process_dev_real_c, numpy.reshape(dev_real_out_c, [len(dev_real_out_c), 1])) 
      map_scores(vf_dir_c, score_dir_c, process_dev_mask_c, numpy.reshape(dev_mask_out_c, [len(dev_mask_out_c), 1]))
      map_scores(vf_dir_c, score_dir_c, process_test_real_c, numpy.reshape(test_real_out_c, [len(test_real_out_c), 1]))
      map_scores(vf_dir_c, score_dir_c, process_test_mask_c, numpy.reshape(test_mask_out_c, [len(test_mask_out_c), 1]))
      map_scores(vf_dir_c, score_dir_c, process_train_real_c, numpy.reshape(train_real_out_c, [len(train_real_out_c), 1]))
      map_scores(vf_dir_c, score_dir_c, process_train_mask_c, numpy.reshape(train_mask_out_c, [len(train_mask_out_c), 1]))
      
      vf_dir_d = os.path.join(args.inputdir+'_d', 'validframes') # input directory with the files with valid frames
      score_dir_d = os.path.join(args.outputdir, 'scores') # output directory for the socre files
      map_scores(vf_dir_d, score_dir_d, process_dev_real_d, numpy.reshape(dev_real_out_d, [len(dev_real_out_d), 1])) 
      map_scores(vf_dir_d, score_dir_d, process_dev_mask_d, numpy.reshape(dev_mask_out_d, [len(dev_mask_out_d), 1]))
      map_scores(vf_dir_d, score_dir_d, process_test_real_d, numpy.reshape(test_real_out_d, [len(test_real_out_d), 1]))
      map_scores(vf_dir_d, score_dir_d, process_test_mask_d, numpy.reshape(test_mask_out_d, [len(test_mask_out_d), 1]))
      map_scores(vf_dir_d, score_dir_d, process_train_real_d, numpy.reshape(train_real_out_d, [len(train_real_out_d), 1]))
      map_scores(vf_dir_d, score_dir_d, process_train_mask_d, numpy.reshape(train_mask_out_d, [len(train_mask_out_d), 1]))
      
    # calculation of the error rates    
    roc_acc_c = roc_acc_c + bob.measure.roc(test_mask_out_c, test_real_out_c,101)    
    roc_acc_d = roc_acc_d + bob.measure.roc(test_mask_out_d, test_real_out_d,101)
    
    thres = bob.measure.eer_threshold(dev_mask_out_c, dev_real_out_c)
    dev_far, dev_frr = bob.measure.farfrr(dev_mask_out_c, dev_real_out_c, thres)
    test_far, test_frr = bob.measure.farfrr(test_mask_out_c, test_real_out_c, thres)
    dev_eer_far_c.append(dev_far)
    dev_eer_frr_c.append(dev_frr)
    test_eer_far_c.append(test_far)
    test_eer_frr_c.append(test_frr)
    
    thres = bob.measure.eer_threshold(dev_mask_out_d, dev_real_out_d)
    dev_far, dev_frr = bob.measure.farfrr(dev_mask_out_d, dev_real_out_d, thres)
    test_far, test_frr = bob.measure.farfrr(test_mask_out_d, test_real_out_d, thres)
    dev_eer_far_d.append(dev_far)
    dev_eer_frr_d.append(dev_frr)
    test_eer_far_d.append(test_far)
    test_eer_frr_d.append(test_frr)
    
    thres = bob.measure.min_hter_threshold(dev_mask_out_c, dev_real_out_c)
    dev_far, dev_frr = bob.measure.farfrr(dev_mask_out_c, dev_real_out_c, thres)
    test_far, test_frr = bob.measure.farfrr(test_mask_out_c, test_real_out_c, thres)
    dev_hter_far_c.append(dev_far)
    dev_hter_frr_c.append(dev_frr)
    test_hter_far_c.append(test_far)
    test_hter_frr_c.append(test_frr)
    
    thres = bob.measure.min_hter_threshold(dev_mask_out_d, dev_real_out_d)
    dev_far, dev_frr = bob.measure.farfrr(dev_mask_out_d, dev_real_out_d, thres)
    test_far, test_frr = bob.measure.farfrr(test_mask_out_d, test_real_out_d, thres)
    dev_hter_far_d.append(dev_far)
    dev_hter_frr_d.append(dev_frr)
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
  tf = open(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_results.txt'), 'w')
  tf.write(txt)
  tf.close()
  
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_eer_c'), (numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_hter_c'), (numpy.array(test_hter_far_c)+numpy.array(test_hter_frr_c))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_eer_d'), (numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_hter_d'), (numpy.array(test_hter_far_d)+numpy.array(test_hter_frr_d))*50)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_roc_c'), roc_acc_c/fold_num*100)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_roc_d'), roc_acc_d/fold_num*100)
  numpy.save(os.path.join(args.outputdir, args.inputdir[-3:]+'_lda_values'), [[numpy.mean((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100, numpy.mean((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100, numpy.mean((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100, numpy.mean((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100],[numpy.std((numpy.array(dev_eer_far_c)+numpy.array(dev_eer_frr_c))/2)*100, numpy.std((numpy.array(test_eer_far_c)+numpy.array(test_eer_frr_c))/2)*100, numpy.std((numpy.array(dev_eer_far_d)+numpy.array(dev_eer_frr_d))/2)*100, numpy.std((numpy.array(test_eer_far_d)+numpy.array(test_eer_frr_d))/2)*100]])
 
if __name__ == '__main__':
  main()
