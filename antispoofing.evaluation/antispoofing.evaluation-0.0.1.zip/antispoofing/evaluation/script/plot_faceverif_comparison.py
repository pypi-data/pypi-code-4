#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Jul 25 20:18:36 CEST 2013

"""Plot DET or EPSC plots to compare 4 face verification systems (GMM, LGBPHS, GJet and ISV) on one figure
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob
import numpy
import argparse
from matplotlib import rc
rc('text',usetex=1)
from matplotlib.ticker import FormatStrFormatter

import matplotlib.font_manager as fm

from ..utils import error_utils

def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('--as', '--antispoof', metavar='STR', type=str, dest='antispoofingalg', default="", help='The antispoofing system', choices=('LBP', 'LBP-TOP-1','MOTION'))
  parser.add_argument('--fu', '--fusion', metavar='STR', type=str, dest='fusionalg', default="", help='The fusion method', choices=('SUM','LLR','LLR_P'))
  parser.add_argument('--bf', '--basedir_faceverif', metavar='STR', type=str, dest='basedir_faceverif', default="", help='The base directory for the baseline face verification algorithms score files (if needed)')
  parser.add_argument('--ba', '--basedir_fvas', metavar='STR', type=str, dest='basedir_fvas', default="", help='The base directory of the fused scores (if needed)')
  parser.add_argument('-b','--baseline', action='store_true', default=False, dest='baseline', help='If True, will plot only the baseline systems for comparison. Otherwise it will plot fused systems based on the specified fusion method')
  parser.add_argument('-s', '--scenario', metavar='STR', type=str, dest='scenario', default="licit", choices=('licit','spoof'), help='The scenario to plot (for DET curve only)')
  parser.add_argument('-t', '--title', metavar='STR', type=str, dest='title', default="", help='Plot title')
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('-o', '--output', metavar='FILE', type=str, default='plots.pdf', dest='output', help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - for DET curve; 2 - for EPSC for HTER_w; 3 - for EPSC for SFAR.')
  
  
  args = parser.parse_args()

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in gray-scale
    color_mapping = {'ubmgmm':'#000000', 'lgbphs':'#4c4c4c', 'ebgm':'#4c4c4c', 'isv':'#999999'}
    marker_mapping = {'ubmgmm':None, 'lgbphs':None, 'ebgm':None, 'isv':None}   
    linestyle_mapping = {'ubmgmm':'--', 'lgbphs':':', 'ebgm':'--', 'isv':'-'}
    width=4
  else: # plot in color
    color_mapping = {'ubmgmm':'blue', 'lgbphs':'green', 'ebgm':'#ff9933', 'isv':'red'}
    marker_mapping = {'ubmgmm':None, 'lgbphs':None, 'ebgm':None, 'isv':None}   
    linestyle_mapping = {'ubmgmm':'-', 'lgbphs':'-', 'ebgm':'-', 'isv':'-'}
    width=4

  legend_dict = {'ubmgmm':'GMM', 'lgbphs':'LGBPHS', 'ebgm':'GJet', 'isv':'ISV'}

  #Plot 1: DET (comparison of baseline systems)
  # -----------
  if args.demandedplot == 1:
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18}) 

    for faceverif in ('ubmgmm', 'lgbphs', 'ebgm', 'isv'):
      if args.baseline:
        base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
      else:
        base_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-eval')
    
      [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
      [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
      [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
      [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

      if args.scenario == 'licit':
        bob.measure.plot.det(base_neg, base_pos, 1000, color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
      else: # args.scenario == 'spoof' 
        bob.measure.plot.det(over_neg, over_pos, 1000, color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
    
    ax1 = mpl.subplot(111); bob.measure.plot.det_axis([0.1, 99, 0.1, 99]); mpl.grid()
     
    mpl.xlabel("False Rejection Rate (\%)");
    mpl.ylabel("False Acceptance Rate (\%)")
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop=fm.FontProperties(size=18))
    mpl.title("DET: comparison of face verification systems" if args.title == "" else args.title)
    pp.savefig()    
  
  
  #Plot 2: EPSC - HTER_w (comparison of baseline systems)
  # -----------
  
  
  if args.demandedplot == 2:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18}) 

    for faceverif in ('ubmgmm','lgbphs', 'ebgm', 'isv'):
      if args.baseline:
        base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
      else:
        base_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-eval')
    
      [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
      [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
      [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
      [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

      weights, thresholds = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points)
      errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thresholds) # error rates are returned in a numpy.ndarrat in the following order: far_w, hter_w
       
      mpl.plot(weights, [100.*k for k in errors[:,1]], color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
      ax1 = mpl.subplot(111);
     
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"HTER$_{\omega}$ (\%)") 
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%.1f')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.title("EPSC: comparison of face verification systems" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()  
  
  #Plot 3: EPSC - SFAR (comparison of baseline systems)
  # -----------
  if args.demandedplot == 3:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18}) 

    for faceverif in ('ubmgmm', 'lgbphs', 'ebgm', 'isv'):
      if args.baseline:
        base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
      else:
        base_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-eval')
    
      [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
      [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
      [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
      [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

      weights, thresholds = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points)
      errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thresholds) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w
       
      mpl.plot(weights, [100.*k for k in errors[:,2]], color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
      ax1 = mpl.subplot(111);
     
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel("SFAR (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.title("EPSC: comparison of face verification systems" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()  
  
    
  # Plot 10: Dummy legend for EPSC plot (doesn't print usefull plot, only there to generate a legend)
  # -------------------------------------------------------------------------------------------------
  if args.demandedplot == 10:
    points = 100
    criteria = 'eer'
    for fusionalg in ('SUM',):
      fig = mpl.figure()
      mpl.rcParams.update({'font.size': 18})
      ax1 = mpl.subplot(111) 
      # Now we are iterating over all the face verification algorithms that need to be plotted on the plot
      for faceverif in ('ubmgmm', 'lgbphs', 'ebgm', 'isv'):

        if args.baseline:
          base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
          over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
          base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
          over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
        else:
          base_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-dev')
          over_dev_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-dev')
          base_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'licit/scores-eval')
          over_test_file = os.path.join(args.basedir_fvas, args.fusionalg, faceverif, args.antispoofingalg, 'spoof/scores-eval')
    
        [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
        [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
        [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
        [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

        weights, thrs = error_utils.epsc_weights(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points)
        errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w

        mpl.plot(weights, [100.*k for k in errors[:,2]], color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
      mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=18))
      mpl.grid()
      pp.savefig()
  
  
  
  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
  


