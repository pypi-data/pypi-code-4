#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Jul 26 18:29:31 CEST 2013

"""Plot DET or EPSC plots to compare 3 fusion methods (SUM, LR and PLR) for a fusing given face verification and anti-spoofing systems
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
  parser.add_argument('--fv', '--faceverif', metavar='STR', type=str, dest='faceverifalg', default="", help='The face-verification system', choices=('ubmgmm','lgbphs','ebgm','isv'))
  parser.add_argument('--bf', '--basedir_faceverif', metavar='STR', type=str, dest='basedir_faceverif', default="", help='The base directory for the baseline face verification algorithms score files')
  parser.add_argument('--ba', '--basedir_fvas', metavar='STR', type=str, dest='basedir_fvas', default="", help='The base directory of the fused scores')
  parser.add_argument('-s', '--scenario', metavar='STR', type=str, dest='scenario', default="licit", choices=('licit','spoof'), help='The scenario to plot (for DET curve only)')
  parser.add_argument('-t', '--title', metavar='STR', type=str, dest='title', default="", help='Plot title')
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('-o', '--output', metavar='FILE', type=str, default='plots.pdf', dest='output', help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - for DET curve; 2 - for EPSC for HTER_w; 3 - for EPSC for SFAR.')

  args = parser.parse_args()

  # Reading the score files for the baseline systems
  base_dev_file = os.path.join(args.basedir_faceverif, args.faceverifalg, 'licit/scores-dev')
  over_dev_file = os.path.join(args.basedir_faceverif, args.faceverifalg, 'spoof/scores-dev')
  base_test_file = os.path.join(args.basedir_faceverif, args.faceverifalg, 'licit/scores-eval')
  over_test_file = os.path.join(args.basedir_faceverif, args.faceverifalg, 'spoof/scores-eval')

  [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
  [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in gray-scale
    color_mapping = {'baseline':'#000000', 'SUM':'#4c4c4c', 'LLR':'#4c4c4c', 'LLR_P':'#999999'}
    linestyle_mapping = {'baseline':'--', 'SUM':':', 'LLR':'--', 'LLR_P':'-'}
    width=4
  else: # plot in color
    color_mapping = {'baseline':'blue','SUM':'red', 'LLR':'green', 'LLR_P':'#ff9933'}
    linestyle_mapping = {'baseline':'-', 'SUM':'-', 'LLR':'-', 'LLR_P':'-'}
    width=4

  fusion_label_dict = {'SUM':'SUM fusion', 'LLR':'LR fusion', 'LLR_P':'PLR fusion'}

  # Plot 1: DET (comparison between baseline systems and systems fused with counter measures)
  # -----------

  # Iteratively, we need to plot the plots using the different antispoofing methods
  if args.demandedplot == 1:
    # Now we are iterating over all the fusion methods that need to be plotted on the plot
    for fusionalg in ('SUM', 'LLR', 'LLR_P'):

      fig = mpl.figure()
      mpl.rcParams.update({'font.size': 18})
      ax1 = mpl.subplot(111)
      base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-dev')
      over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-dev')
      base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-eval')
      over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-eval')

      [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
      [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
      [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
      [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

      bob.measure.plot.det(base_neg_cm, base_pos_cm, 1000, color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label=fusion_label_dict[fusionalg])
      bob.measure.plot.det(over_neg_cm, over_pos_cm, 1000, color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label=fusion_label_dict[fusionalg])

      bob.measure.plot.det_axis([0.1, 99, 0.1, 99]); mpl.grid()
      mpl.xlabel("False Rejection Rate (\%)")
      mpl.ylabel("False Acceptance Rate (\%)")
    
      mpl.legend(prop=fm.FontProperties(size=18))
      mpl.grid()
      pp.savefig()
      
      
  # Plot 2: EPSC - HTER(comparison between baseline and fused counter measures)
  # -----------
  if args.demandedplot == 2:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    ax1 = mpl.subplot(111) 
      
    weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria)
    errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # error rates are returned in a numpy.ndarrat in the following order: far_w, hter_w
    # plotting the baseline scores
    mpl.plot(weights, [100.*k for k in errors[:,1]], color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=width, label = 'baseline')

    # Now we are iterating over all the fusion methods that need to be plotted on the plot
    for fusionalg in ('SUM', 'LLR', 'LLR_P'):

      base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-dev')
      over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-dev')
      base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-eval')
      over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-eval')
      
      [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
      [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
      [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
      [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

      weights, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria)
      errors_cm = error_utils.epsc_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, weights, thrs_cm) # error rates are returned in a numpy.ndarrat in the following order: far_w, hter_w

      mpl.plot(weights, [100.*k for k in errors_cm[:,1]], color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
      mpl.ylim(ymax=30)
      
    mpl.xlabel("Weight $\omega$");
    mpl.ylabel(r"HTER$_{\omega}$ (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode=r"expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.grid()
    pp.savefig()
      
  # Plot 3: EPSC - SFAR (comparison between baseline and fused counter measures)
  # -----------
  if args.demandedplot == 3:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    ax1 = mpl.subplot(111) 
      
    weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria)
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w
    # plotting the baseline scores
    mpl.plot(weights, [100.*k for k in errors[:,2]], color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=4, label = 'baseline')

    # Now we are iterating over all the fusion methods that need to be plotted on the plot
    for fusionalg in ('SUM', 'LLR', 'LLR_P'):

      base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-dev')
      over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-dev')
      base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-eval')
      over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-eval')
  
      [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
      [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
      [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
      [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

      weights, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria)
      errors_cm = error_utils.all_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, weights, thrs_cm) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w

      mpl.plot(weights, [100.*k for k in errors_cm[:,2]], color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
      mpl.ylim(ymax=100)
      
    mpl.xlabel("Weight $\omega$");
    mpl.ylabel(r"SFAR (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode=r"expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.grid()
    pp.savefig()
    
    
  # Plot 10: Dummy legend for EPSC plot (doesn't print usefull plot, only there to generate a legend)
  # -------------------------------------------------------------------------------------------------
  if args.demandedplot == 10:
    for antispoofingalg in ('LBP',):
      points = 100
      criteria = 'eer'
      fig = mpl.figure()
      mpl.rcParams.update({'font.size': 18})
      ax1 = mpl.subplot(111) 
      weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria)
      errors = error_utils.spoofing_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # errors are returned in a numpy.ndarray in the following order: FRR, FAR (impostors), HTER (licit), SFAR
      # plotting the baseline scores
      mpl.plot(weights, [100.*k for k in errors[:,3]], color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], label = 'baseline')  

      # Now we are iterating over all the fusion methods that need to be plotted on the plot
      for fusionalg in ('SUM','LLR', 'LLR_P'):

        base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-dev')
        over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-dev')
        base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'licit/scores-eval')
        over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, args.faceverifalg, args.antispoofingalg, 'spoof/scores-eval')
  
        [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
        [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
        [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
        [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

        weights, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria)
        errors_cm = error_utils.all_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, weights, thrs_cm) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w

        mpl.plot(weights, [100.*k for k in errors_cm[:,2]], color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
      
      mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
      mpl.grid()
      pp.savefig()    
  
  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
  


