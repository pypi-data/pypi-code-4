#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Plots the bar charts for anti-spoofing results for different LBP types and classifiers for 3DMAD
"""

import os, sys
import argparse
import bob
import numpy
import matplotlib.pyplot
import mpl_toolkits.axisartist as AA
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'result', 'antispoof')
  OUTPUT_DIR = os.path.join(basedir, 'result')
  
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the result files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--output-dir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  args = parser.parse_args()
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  
  data_types = ['grayscale','depth']
  lbp_types = ['regular','bl_regular','transitional','bl_transitional','direction_coded','bl_direction_coded','modified','bl_modified', 'maatta11']
  cls_types = ['chi2','lda','svm']

  f = matplotlib.pyplot.figure(num=None, figsize=(9, 4.5), dpi=100, facecolor='w')
  ax1 = AA.Subplot(f,211)
  ax2 = AA.Subplot(f,212)
  f.add_subplot(ax1)
  f.add_subplot(ax2)
  ax1.axis["right"].set_visible(False)
  ax1.axis["bottom"].set_visible(False)
  ax2.axis["right"].set_visible(False)
  ax2.axis["top"].set_visible(False)
  width = 1
  
  for d in data_types:
    ind = 0
    for l in lbp_types:  
      for c in cls_types:
        file_name = os.path.join(args.inputdir,d,l+'_'+c+'.hdf5')
        if os.path.exists(file_name):
          file_hdf5 = bob.io.HDF5File(str(file_name))
          DEER = file_hdf5.read('Dev_EER')
          THTER = file_hdf5.read('Test_HTER')          
          avg_deer = numpy.mean(DEER)
          std_deer = numpy.std(DEER)
          avg_thter = numpy.mean(THTER)
          std_thter = numpy.std(THTER)
          print d, l, c
          print 'Dev  EER  mean: %4.2f std: %4.2f' %(avg_deer, std_deer)
          print 'Test HTER mean: %4.2f std: %4.2f' %(avg_thter, std_thter)
          if d == 'grayscale':
            b1 = ax1.bar(ind, avg_deer, width, yerr=std_deer, ecolor='k', color = '#990000', edgecolor = 'white')
            b2 = ax1.bar(ind+1, avg_thter, width, yerr=std_thter, ecolor='k', color = '#00cc66', edgecolor = 'white')
          else:
            ax2.bar(ind, avg_deer, width, yerr=std_deer, ecolor='k', color = '#990000', edgecolor = 'white')
            ax2.bar(ind+1, avg_thter, width, yerr=std_thter, ecolor='k', color = '#00cc66', edgecolor = 'white')
          ind = ind+2
      ind = ind+2

  ax1.set_ylabel('HTER for Color')
  ax1.tick_params(axis='x', bottom='off', top='off')
  ax1.tick_params(axis='y', right='off', direction='out')
  ax1.set_xlim(-1,72)
  ax1.set_ylim(-9,55)
  ind = numpy.array([2,10,18,26,34,42,50,58,67])
  ax1.set_xticks(ind+width+0.5)
  ax1.set_xticklabels(['LBP(I)','LBP(B)','tLBP(I)','tLBP(B)','dLBP(I)','dLBP(B)','mLBP(I)','mLBP(B)','Multiscale'])
  ax1.axis["top"].line.set_visible(False)
  ax1.axis["top"].major_ticks.set_visible(False)
  ax1.axis["top"].major_ticklabels.set_visible(True)
  ax1.axis["top"].major_ticklabels.set_rotation(0)
  ax1.axis["top"].set_ticklabel_direction('+')
  ax1.axis["top"].major_ticklabels.set_pad(-5)
  
  ax2.set_ylabel('HTER for Depth')
  ax2.tick_params(axis='x', bottom='off', top='off')
  ax2.tick_params(axis='y', right='off', direction='out')
  ax2.set_xlim(-1,72)
  ax2.set_ylim(-9,55)
  ind = numpy.array([0,2,4,8,10,12,16,18,20,24,26,28,32,34,36,40,42,44,48,50,52,56,58,60,64,66,68])
  ax2.set_xticks(ind+width+0.5)
  ax2.set_xticklabels([r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM',r'$\chi^2$','LDA','SVM'])
  ax2.axis["bottom"].major_ticklabels.set_rotation(90)
  ax2.axis["bottom"].major_ticks.set_visible(False)
  ax2.axis["bottom"].line.set_visible(False)
  
  l = matplotlib.pyplot.figlegend((b1,b2),('Dev. Set','Test Set'),(0.8, 0.4))
  l.draw_frame(False)
  
  file_name = os.path.join(args.outputdir,'antispoof.png')
  matplotlib.pyplot.savefig(file_name)
  
  return 0

if __name__ == "__main__":
  main()
