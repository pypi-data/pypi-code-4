#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Runs the LBP algorithm on 2D or 2.5D images taking each mask in 3DMAD database separately as the test set, in leave-one-out manner.
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

def create_full_dataset(indir, ftdir, objects):
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
        ft = lbphist(image2)
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
  
def divideframe(frame):
  blockslist = [] 
  size = [6,8,8,8,8,8,8,6]
  for x in range(0,8):
    for y in range(0,8):
      w = size[x]
      h = size[y]
      sx = sum(size[0:x])
      sy = sum(size[0:y])
      nextblock = frame[sx:sx+w, sy:sy+h]
      blockslist.append(nextblock)
  return blockslist # list of subblocks as frames
  
def lbphist(img):
  norm = False
  finalhist = numpy.array([])
  lbp = bob.ip.LBP(8,2,2,uniform=True) 
  lbpimage = numpy.ndarray(lbp.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes
  lbp(img, lbpimage) # calculating the lbp image
  blockslist = divideframe(lbpimage) # divide the lbp image into 8x8 blocks
  for bl in blockslist:
    hist = bob.ip.histogram(bl, 0, lbp.max_label-1, lbp.max_label)
    if norm:
      hist = hist / sum(hist) # histogram normalization
    finalhist = numpy.append(finalhist, hist) # concatenate the subblocks' already normalized histograms
  return finalhist

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
  ftdir = os.path.join(FEATURE_DIR,'LBP',args.type)
  
  inputdir = os.path.join(args.inputdir,args.type)
  if not os.path.exists(inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  make_sure_path_exists(os.path.join(args.outputdir,'LBP_'+args.type))
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
    
    file_name = os.path.join(args.outputdir,'LBP_'+args.type,str(mask).zfill(2)+'.hdf5')
    if not os.path.exists(file_name):
      print 'Extracting/loading LBP features for mask #%d..' %mask
      # No training is required.
      dev_enrol_lbp = create_full_dataset(inputdir,ftdir,dev_enrol)
      dev_probe_real_lbp = create_full_dataset(inputdir,ftdir,dev_probe_real)
      test_enrol_lbp = create_full_dataset(inputdir,ftdir,test_enrol)
      test_probe_mask_lbp = create_full_dataset(inputdir,ftdir,test_probe_mask)
      test_probe_real_lbp = create_full_dataset(inputdir,ftdir,test_probe_real)
      
      print 'Matching and calculating scores..'    
      dev_scores_real = numpy.zeros((len(dev_probe_real_lbp),len(dev_enrol_lbp)))
      dev_impostor = []
      dev_genuine = []
      for e in range(0,len(dev_enrol_lbp)):
        hist1 = dev_enrol_lbp[e,:]
        for p in range(0,len(dev_probe_real_lbp)):
          hist2 = dev_probe_real_lbp[p,:]
          score = -1*bob.math.chi_square(hist1, hist2)
          dev_scores_real[p,e] = score
          if p/50 == e/50:
            dev_genuine.append(score)
          else:
            dev_impostor.append(score)
     
      test_scores_real = numpy.zeros((len(test_probe_real_lbp),len(test_enrol_lbp)))
      test_genuine = []
      for e in range(0,len(test_enrol_lbp)):
        hist1 = test_enrol_lbp[e,:]
        for p in range(0,len(test_probe_real_lbp)):
          hist2 = test_probe_real_lbp[p,:]
          score = -1*bob.math.chi_square(hist1, hist2)
          test_scores_real[p,e] = score
          test_genuine.append(score)
     
      test_scores_mask = numpy.zeros((len(test_probe_mask_lbp),len(test_enrol_lbp)))
      test_mask = []
      for e in range(0,len(test_enrol_lbp)):
        hist1 = test_enrol_lbp[e,:]
        for p in range(0,len(test_probe_mask_lbp)):
          hist2 = test_probe_mask_lbp[p,:]
          score = -1*bob.math.chi_square(hist1, hist2)
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
    
    file_name = os.path.join(args.outputdir,'LBP_'+args.type,str(mask).zfill(2)+'.png')
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
