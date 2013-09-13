#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Feb 18 16:12:41 CET 2013

"""Plot different types of plots as demanded by the user. The numbers of the plots to be plotted are given as a command line argument. 
"""

import os
import sys
from matplotlib import rc
rc('text',usetex=1)
import matplotlib.pyplot as mpl
import bob
import numpy as np
import argparse

import matplotlib.font_manager as fm

from ..utils import error_utils


def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('baseline_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (development set)')
  parser.add_argument('baseline_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (test set)')
  parser.add_argument('overlay_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; development set)')
  parser.add_argument('overlay_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; test set)')
  parser.add_argument('-b', '--type-of-threshold', metavar='STR', type=str,
      dest='threshold', default="hter", help='Type of threshold', choices=('eer', 'hter'))
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('--norealdata', action='store_true',help='If True, will annotate the plots hypothetically, instead of with real data values of the calculated error rates.')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - for DET for licit scenario only; 2 - for DET for licit and spoof scenario; 3 - for DET for licit and spoof scenario and FRR line; 4 - for score distribution for licit scenario; 5 - for score distribution for licit scenario and threshold line; 6 - for score distribution for licit and spoof scneario and threshold line; 7 - for score distribution for licit and spoof scenario and threshold line and probability of success line; 8 - for EPC for licit scenario; 9 - for EPC for licit scenario and SFAR line; 10 - for EPSC for HTER-w; 11 - for EPSC for SFAR.', nargs='+')

  args = parser.parse_args()

  if args.threshold == 'eer':
    report_text = "EER"
  else:
    report_text = "Min.HTER"

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  # setting up the color and style-schemes
  if args.nocolor: # plot in grey-scale
    color_scheme = {'genuine':'black', 'impostors':'black', 'spoofs':'white', 'line':'black'}
    linestyle_scheme = {'line1':'-', 'line2':'dotted'}
    linecolor_scheme = {'line1':'black', 'line2':'black'}
    alpha_scheme = {'genuine':0.4, 'impostors':0.8, 'spoofs':0.6}
    hatch_scheme = {'genuine':None, 'impostors':None, 'spoofs':'//'} 
  else: # plot in color  
    color_scheme = {'genuine':'blue', 'impostors':'red', 'spoofs':'black', 'line':'green'}
    linestyle_scheme = {'line1':'-', 'line2':'-'}
    linecolor_scheme = {'line1':'blue', 'line2':'red'}
    alpha_scheme = {'genuine':0.6, 'impostors':0.8, 'spoofs':0.4}
    hatch_scheme = {'genuine':None, 'impostors':None, 'spoofs':None}    


  # Plot 1: DET (LICIT scenario only)
  # -------------------------
  if 1 in args.demandedplot:
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    bob.measure.plot.det(base_neg, base_pos, 100, color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], linewidth=4)
    bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
    mpl.title("DET: baseline verification system" if args.title == "" else args.title)
    mpl.xlabel("False Positive Rate (\\%)")
    mpl.ylabel("False Negative Rate (\\%)")
    mpl.grid()
    pp.savefig()


  # Plot 2: DET (LICIT + SPOOF SCENARIO)
  # ------------------------------------

  if 2 in args.demandedplot:
    fig = mpl.figure()
    bob.measure.plot.det(base_neg, base_pos, 100, color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label="LICIT", linewidth=4)
    bob.measure.plot.det(over_neg, over_pos, 100, color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label="SPOOF", linewidth=4)
    bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
    mpl.title("DET: LICIT and overlaid SPOOF scenario" if args.title == "" else args.title)
    mpl.xlabel("False Rejection Rate (\%)")
    mpl.ylabel("False Acceptance Rate (\%)")
    mpl.legend()
    mpl.grid()
    pp.savefig()


  # Plot 3: DET (LICIT + SPOOF scenario) + threshold at fixed FRR
  # ------------------------------------

  if 3 in args.demandedplot:
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    bob.measure.plot.det(base_neg, base_pos, 100, color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label="Licit scenario", linewidth=4)
    bob.measure.plot.det(over_neg, over_pos, 100, color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label="Spoof scenario", linewidth=4)
    bob.measure.plot.det_axis([0.01, 99, 0.01, 99])
    ax = mpl.subplot(111)
    mpl.rcParams.update({'font.size': 18}) 
    if args.threshold == 'eer':
      thres_baseline = bob.measure.eer_threshold(base_neg_dev, base_pos_dev)
    else:
      thres_baseline = bob.measure.min_hter_threshold(base_neg_dev, base_pos_dev)

    axlim = mpl.axis()

    farfrr_licit = bob.measure.farfrr(base_neg, base_pos, thres_baseline) # calculate test frr @ EER (licit scenario)
    farfrr_spoof = bob.measure.farfrr(over_neg, over_pos, thres_baseline) # calculate test frr @ EER (spoof scenario)
    farfrr_licit_det = [bob.measure.ppndf(i) for i in farfrr_licit] # find the FAR and FRR values that need to be plotted on normal deviate scale
    farfrr_spoof_det = [bob.measure.ppndf(i) for i in farfrr_spoof] # find the FAR and FRR values that need to be plotted on normal deviate scale
    if args.norealdata:
      mpl.axvline(x=farfrr_licit_det[1], ymin=axlim[2], ymax=axlim[3], color='k', linestyle='--', linewidth = 4, label="FRR @ EER") # vertical FRR threshold
    else:
      mpl.axvline(x=farfrr_licit_det[1], ymin=axlim[2], ymax=axlim[3], color='k', linestyle='--', linewidth = 4, label="FRR = %.2f\\%%" % (farfrr_licit[1]*100)) # vertical FRR threshold
    mpl.plot(farfrr_licit_det[1], farfrr_licit_det[0], 'o', color=linecolor_scheme['line1'], markersize=8) # FAR point, licit scenario
    mpl.plot(farfrr_spoof_det[1], farfrr_spoof_det[0], 'o', color=linecolor_scheme['line2'], markersize=8) # FAR point, spoof scenario

    # annotate the FAR points
    xyannotate_licit = [bob.measure.ppndf(1.4*farfrr_licit[0]), bob.measure.ppndf(1.2*farfrr_licit[1])]
    xyannotate_spoof = [bob.measure.ppndf(1*farfrr_spoof[0]), bob.measure.ppndf(1.2*farfrr_licit[1])]
    #mpl.annotate('FAR @ operating point', xy=(farfrr_licit_det[1], farfrr_licit_det[0]),  xycoords='data', xytext=(xyannotate_licit[1], xyannotate_licit[0]), color=linecolor_scheme['line1'])
    #mpl.annotate('SFAR @ operating point', xy=(farfrr_spoof_det[1], farfrr_spoof_det[0]),  xycoords='data', xytext=(xyannotate_spoof[1], xyannotate_spoof[0]), color=linecolor_scheme['line2'])
    mpl.annotate('FAR = %.2f\\%%' % (farfrr_licit[0]*100), xy=(farfrr_licit_det[1], farfrr_licit_det[0]),  xycoords='data', xytext=(xyannotate_licit[1], xyannotate_licit[0]), color=linecolor_scheme['line1'], size='large')
    mpl.annotate('SFAR = %.2f\\%%' % (farfrr_spoof[0]*100), xy=(farfrr_spoof_det[1], farfrr_spoof_det[0]),  xycoords='data', xytext=(xyannotate_spoof[1], xyannotate_spoof[0]), color=linecolor_scheme['line2'], size='large')

    mpl.tick_params(axis='both', which='major', labelsize=4)

    mpl.title("DET: LICIT and overlaid SPOOF scenario" if args.title == "" else args.title)
    mpl.xlabel("False Rejection Rate (\%)")
    mpl.ylabel("False Acceptance Rate (\%)")
    mpl.legend(prop=fm.FontProperties(size=18))
    
    for tick in ax.xaxis.get_major_ticks():
      tick.label.set_fontsize(6) 
    for tick in ax.yaxis.get_major_ticks():
      tick.label.set_fontsize(6) 
    
    mpl.grid()
    pp.savefig()

  
  # Plot 4: Score histograms (LICIT only)
  # --------------------------

  if 4 in args.demandedplot:
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
    mpl.rcParams.update({'font.size': 18})
  
    mpl.hist(base_pos, bins=10, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'], label="Genuine users", normed=True)
    mpl.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'], label="Impostors", normed=True) 

    mpl.xlabel("Scores")
    mpl.ylabel("Normalized Count")

    mpl.legend(prop=fm.FontProperties(size=18))

    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.title("Score distributions of verification system" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()

  # Plot 5: Score histograms + Threshold (LICIT only)
  # --------------------------------------

  if 5 in args.demandedplot:
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
    mpl.rcParams.update({'font.size': 18})
  
    mpl.hist(base_pos, bins=10, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'], label="Genuine users", normed=True)
    mpl.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'], label="Impostors", normed=True)
    
    axlim = mpl.axis()

    if args.threshold == 'eer':
      thres_baseline = bob.measure.eer_threshold(base_neg_dev, base_pos_dev)
    else:
      thres_baseline = bob.measure.min_hter_threshold(base_neg_dev, base_pos_dev)

    # plot the threshold line
    mpl.axvline(x=thres_baseline, ymin=0, ymax=1, linewidth=4, color=color_scheme['line'], linestyle='--', label="threshold")
  
    mpl.xlabel("Scores")
    mpl.ylabel("Normalized Count")
    
    mpl.legend(prop=fm.FontProperties(size=18))

    mpl.title("Score distributions of verification system" if args.title == "" else args.title)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()
    pp.savefig()

  # Plot 6: Score histograms + threshold (LICIT + SPOOF)
  # ------------------------------------------
  if 6 in args.demandedplot:
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
     
    mpl.rcParams.update({'font.size': 18})
    mpl.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'],
      label="Impostors", normed=True)
    mpl.hist(base_pos, bins=10, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'],
      label="Genuine Users", normed=True)
    mpl.hist(over_neg, bins=10, color=color_scheme['spoofs'], alpha=alpha_scheme['spoofs'], hatch=hatch_scheme['spoofs'],
      label="Spoofing Attacks", normed=True)

    axlim = mpl.axis()

    if args.threshold == 'eer':
      thres_baseline = bob.measure.eer_threshold(base_neg_dev, base_pos_dev)
    else:
      thres_baseline = bob.measure.min_hter_threshold(base_neg_dev, base_pos_dev)

    # plot the line
    mpl.axvline(x=thres_baseline, ymin=0, ymax=1, linewidth=4, color=color_scheme['line'], linestyle='--', label="threshold")
  
    mpl.xlabel("Verification Scores")
    mpl.ylabel("Normalized Count")
    mpl.legend(prop=fm.FontProperties(size=18))

    mpl.title("Score distributions of verification system" if args.title == "" else args.title)
    frame1 = mpl.gca()
    #frame1.axes.get_xaxis().set_ticks([])
    #frame1.axes.get_yaxis().set_ticks([])

    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties) 
    mpl.grid()
    pp.savefig()

  # Plot 7: Score histogram (LICIT + SPOOF) + Probability of Success line
  # --------------------------------------------

  if 7 in args.demandedplot:
    fig = mpl.figure()
    ax1 = mpl.subplot(111)

    #base_pos = base_pos / 100000; base_neg = base_neg / 100000; # to be used if the scores are not normalized
    #over_pos = over_pos / 100000; over_neg = over_neg / 100000;
    #base_pos_dev = base_pos_dev / 100000; base_neg_dev = base_neg_dev / 100000;
    #over_pos_dev = over_pos_dev / 100000; over_neg_dev = over_neg_dev / 100000;
    
    mpl.rcParams.update({'font.size': 18}) 
    mpl.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'],
      label="Impostors", normed=True)
    mpl.hist(base_pos, bins=20, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'],
      label="Genuine Users", normed=True)
    mpl.hist(over_neg, bins=20, color=color_scheme['spoofs'], alpha=alpha_scheme['spoofs'], hatch=hatch_scheme['spoofs'],
      label="Spoofing Attacks", normed=True)

    axlim = mpl.axis()
    
    if args.threshold == 'eer':
      thres_baseline = bob.measure.eer_threshold(base_neg_dev, base_pos_dev)
    else:
      thres_baseline = bob.measure.min_hter_threshold(base_neg_dev, base_pos_dev)
    pass_rate = error_utils.calc_pass_rate(thres_baseline, over_neg)
    
    threscolor = color_scheme['line']
    mpl.axvline(x=thres_baseline, ymin=0, ymax=1, linewidth=4,
      color=color_scheme['line'], linestyle='--', label="threshold")
  
    mpl.xlabel("Verification Scores")
    mpl.ylabel("Normalized Count")
    mpl.legend(prop=fm.FontProperties(size=16), loc = 2)

    # scan the range of scores, put an axis on the right with spoofing success
    # probabilities that depend on the threshold
    ntick = 100
    step = (axlim[1] - axlim[0])/float(ntick)
    thres = [(k*step)+axlim[0] for k in range(ntick)]
    mix_prob_y = []
    for k in thres: mix_prob_y.append(100.*calc_pass_rate(k, over_neg))

    prob_ax = ax1.twinx() 
    mpl.plot(thres, mix_prob_y, color=color_scheme['line'], label="SFAR", linewidth=4)
    prob_ax.set_ylabel("SFAR (\%)", color=color_scheme['line'])
    for tl in prob_ax.get_yticklabels(): tl.set_color(color_scheme['line'])

    # Inprint the threshold one on the plot:
    prob_ax.plot(thres_baseline, 100.*pass_rate, 'o', markersize=10, color=threscolor)
    if args.norealdata:
      prob_ax.text(thres_baseline-(thres_baseline-axlim[0])/2.3, 95.*pass_rate, 'SFAR @ operating point', color='green',size='small',multialignment='right')
    else:
      prob_ax.text(thres_baseline+(thres_baseline-axlim[0])/10, 95.*pass_rate, '%.1f\\%%' % (100.*pass_rate,), color=color_scheme['line'])
      #prob_ax.annotate('%.1f\\%%' % (100.*pass_rate,), xy=(thres_baseline, 100.*pass_rate),  xycoords='data', xytext=(0.3, 0.3), textcoords='axes fraction', color=color_scheme['line'], size='large', arrowprops=dict(facecolor='black', shrink=0.05, width=2), horizontalalignment='right', verticalalignment='top',)

    mpl.title("Score distributions of verification system" if args.title == "" else args.title)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties) 
    prob_ax.set_yticklabels(prob_ax.get_yticks(), fontProperties) 
    from matplotlib.ticker import FormatStrFormatter
    majorFormatter = FormatStrFormatter('%d')
    prob_ax.yaxis.set_major_formatter(majorFormatter)
    ax1.xaxis.set_major_formatter(majorFormatter)

    mpl.grid()
    pp.savefig()
    
    
  # Plot 8: EPC
  #-------------
  if 8 in args.demandedplot:
    mpl.rcParams.update({'font.size': 18})
    epc_baseline = error_utils.epc(base_neg_dev, base_pos_dev, base_neg, base_pos, 100)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
  
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
    mpl.plot(epc_baseline[:,0], [100.*k for k in epc_baseline[:,1]],
      color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], linewidth=4)

    mpl.xlabel(r"Weight $\beta$")
    ax1.set_ylabel("WER (\%)")
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.title("EPC" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()  
    

  # Plot 9: EPC (LICIT + SFAR for SPOOF scenario)
  # -------------------------------------------------

  if 9 in args.demandedplot:
  
    epc_baseline = error_utils.epc(base_neg_dev, base_pos_dev, base_neg, base_pos, 100)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
    mpl.rcParams.update({'font.size': 18})
    
    mpl.plot([],[],color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], linewidth=4, label=r"WER")
    mpl.plot([],[],color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], linewidth=4, label = 'SFAR')
    mpl.legend(prop=fm.FontProperties(size=18))
    
    mpl.plot(epc_baseline[:,0], [100.*k for k in epc_baseline[:,1]], color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label='WER', linewidth=4)

    mpl.xlabel(r"Weight $\beta$")
    ax1.set_ylabel("WER (\%)", color=linecolor_scheme['line1'])
    for tl in ax1.get_yticklabels(): tl.set_color(linecolor_scheme['line1'])

    mix_prob_y = []
    for k in epc_baseline[:,2]:
      prob_attack = sum(1 for i in over_neg if i >= k)/float(over_neg.size)
      mix_prob_y.append(100.*prob_attack)

    axlim = mpl.axis()
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    prob_ax = ax1.twinx() 
    prob_ax.set_xticklabels(prob_ax.get_yticks(), fontProperties)
    prob_ax.set_yticklabels(prob_ax.get_yticks(), fontProperties)
    mpl.plot(epc_baseline[:,0], mix_prob_y, color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label="SFAR", linewidth=4)
    prob_ax.set_ylabel("SFAR (\%)", color=linecolor_scheme['line2'])
    for tl in prob_ax.get_yticklabels(): tl.set_color(linecolor_scheme['line2'])

    mpl.title("EPC and SFAR" if args.title == "" else args.title)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    prob_ax.set_yticklabels(prob_ax.get_yticks(), fontProperties)
    ylabels = prob_ax.get_yticks()
    prob_ax.yaxis.set_ticklabels(["%.0f" % val for val in ylabels])
    mpl.grid()
    pp.savefig()

  # Plot 10: EPSC - HTER-w
  # -------------------------------------------------
  
  if 10 in args.demandedplot:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria)
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w
    
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    mpl.plot(weights, [100.*k for k in errors[:,4]], color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = r"HTER$_\omega$",linewidth=4)
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"HTER$_{\omega}$ (\%)")

    mpl.title("EPSC" if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
   
  # Plot 11: EPSC - SFAR
  # -------------------------------------------------
  
  if 11 in args.demandedplot:
    points = 100
    criteria = 'eer'
    fig = mpl.figure()
    weights, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria)
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, weights, thrs) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, hter_w
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    mpl.plot(weights, [100.*k for k in errors[:,2]], color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label = 'SFAR', linewidth=4)
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel("SFAR (\%)")

    mpl.title("EPSC" if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()    
    
    
  # Plot 15: Dummy legend for histogram plot (doesn't print usefull plot, only there to generate a legend)
  # ------------------------------------------
  if 15 in args.demandedplot:
    fig = mpl.figure()
    ax1 = mpl.subplot(111)
  
    mpl.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'],
      label="Impostors", normed=True)
    mpl.hist(base_pos, bins=10, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'],
      label="Genuine Users", normed=True)
    mpl.hist(over_neg, bins=10, color=color_scheme['spoofs'], alpha=alpha_scheme['spoofs'], hatch=hatch_scheme['spoofs'],
      label="Spoofing Attacks", normed=True)

    axlim = mpl.axis()

    if args.threshold == 'eer':
      thres_baseline = bob.measure.eer_threshold(base_neg_dev, base_pos_dev)
    else:
      thres_baseline = bob.measure.min_hter_threshold(base_neg_dev, base_pos_dev)

    # plot the line
    mpl.axvline(x=thres_baseline, ymin=0, ymax=0, linewidth=4,
      color=color_scheme['line'], linestyle='--', label="threshold")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    mpl.grid()
    pp.savefig()    
    
  pp.close() # close multi-page PDF writer
 

if __name__ == '__main__':
  main()
