#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <Nesli.Erdogmus@gmail.com>
# Mon 17 Jun 16:46:39 2013 

"""Plots the bar charts for verification and spoofing results all masks in 3DMAD
"""

import os, sys
import argparse
import bob
import numpy
import matplotlib.pyplot
import errno

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'result')
  OUTPUT_DIR = os.path.join(basedir, 'result')
  
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the result files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--output-dir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-a', '--algorithm', dest="algorithm", default='LBP', choices=('LBP', 'ISV', 'TPS', 'ICP'), help="Type of algprithm to be analyzed (defaults to '%(default)s')")
  parser.add_argument('-t', '--type', dest="type", default='grayscale', choices=('grayscale', 'depth'), help="Type of input images to be analyzed for LBP and ISV methods(defaults to '%(default)s')")
  parser.add_argument('-r', dest='frr', default=False, action='store_true', help='If set, the false rejection rates for test set will also be plotted.')
  
  args = parser.parse_args()
  
  if args.algorithm == 'TPS' or args.algorithm == 'ICP':
    args.type = 'accumulated'
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")
  if not os.path.exists(os.path.join(args.inputdir,args.algorithm+'_'+args.type)):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(args.outputdir)
  
  EER = []
  SFAR = []
  SFRR = []
  
  for mask in range(1,18):
    file_name = os.path.join(args.inputdir,args.algorithm+'_'+args.type,str(mask).zfill(2)+'.hdf5')
    file_hdf5 = bob.io.HDF5File(str(file_name))
    
    dev_genuine = file_hdf5.read('Dev_Genuine')
    dev_impostor = file_hdf5.read('Dev_Impostor')
    test_genuine = file_hdf5.read('Test_Genuine')
    test_mask = file_hdf5.read('Test_Mask')
    
    t_eer = bob.measure.eer_threshold(dev_impostor, dev_genuine)
    far,frr = bob.measure.farfrr(dev_impostor, dev_genuine, t_eer)
    sfar,sfrr = bob.measure.farfrr(test_mask, test_genuine, t_eer)
    EER.append(far*100)
    SFAR.append(sfar*100)
    SFRR.append(sfrr*100)
  
  print 'EER:', ['%4.2f' % val for val in EER]
  print 'SFAR:', ['%4.2f' % val for val in SFAR]
  print 'SFRR:', ['%4.2f' % val for val in SFRR]
  print 'Average EER:', sum(EER)/17
  print 'Average SFAR:', sum(SFAR)/17
  print 'Std for EER:', numpy.std(EER)
  
  fig = matplotlib.pyplot.figure()
  title =  'EER (avg: %.1f%%) and SFAR (avg: %.1f%%)' %(sum(EER)/17, sum(SFAR)/17)
  matplotlib.pyplot.title(title, fontsize=20)
  matplotlib.pyplot.xlabel('Masks', fontsize=20)
  if args.frr:
    matplotlib.pyplot.ylabel('EER / SFAR / SFRR', fontsize=20)
    rng1 = numpy.array(range(0,17))+0.7
    rng2 = numpy.array(range(0,17))+0.9
    rng3 = numpy.array(range(0,17))+1.1
    p1 = matplotlib.pyplot.bar(rng1,EER,width=0.2,label='EER')
    p2 = matplotlib.pyplot.bar(rng2,SFAR,width=0.2,label='SFAR',color='r')
    p3 = matplotlib.pyplot.bar(rng3,SFRR,width=0.2,label='SFRR',color='g')
  else:
    matplotlib.pyplot.ylabel('EER / SFAR', fontsize=20)
    rng1 = numpy.array(range(0,17))+0.6
    rng2 = numpy.array(range(0,17))+1.0
    p1 = matplotlib.pyplot.bar(rng1,EER,width=0.4,label='EER')
    p2 = matplotlib.pyplot.bar(rng2,SFAR,width=0.4,label='SFAR',color='r')
    
  matplotlib.pyplot.xticks(numpy.arange(1,18,1))
  matplotlib.pyplot.yticks(numpy.arange(0,101,10))
  matplotlib.pyplot.grid()
  matplotlib.pyplot.legend(prop={'size':17})
  file_name = os.path.join(args.outputdir,args.algorithm+'_'+args.type+'.png')
  matplotlib.pyplot.savefig(file_name, bbox_inches='tight')
  
  return 0

if __name__ == "__main__":
  main()  
