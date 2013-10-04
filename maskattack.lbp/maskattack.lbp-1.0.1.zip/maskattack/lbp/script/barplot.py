import os, sys
import argparse
import numpy
import matplotlib
if not hasattr(matplotlib, 'backends'): matplotlib.use('pdf')
import matplotlib.pyplot
import mpl_toolkits.axisartist as AA

def main():
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'res')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-id', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the result files to be plotted by this procedure (defaults to "%(default)s")')
  args = parser.parse_args()
  
  path = args.inputdir
  lbp_types = ['r_1','r_3','d_1','d_3','m_1','m_3','t_1','t_3']
  cls_types = ['cmp','svm','lda']

  f = matplotlib.pyplot.figure(num=None, figsize=(9, 4.5), dpi=100, facecolor='w')
  ax1 = AA.Subplot(f,211)
  ax2 = AA.Subplot(f,212)
  f.add_subplot(ax1)
  f.add_subplot(ax2)
  ax1.axis["right"].set_visible(False)
  #ax1.axis["top"].set_visible(False)
  ax1.axis["bottom"].set_visible(False)
  ax2.axis["right"].set_visible(False)
  ax2.axis["top"].set_visible(False)
  width = 1
  ind = 0
  for l in lbp_types:  
    for c in cls_types:
      file_name = os.path.join(path,l+'_'+c+'_values.npy')
      val = numpy.array(numpy.load(file_name))
      b1 = ax1.bar(ind, val[0,0], width, yerr=val[1,0], ecolor='k', color = '0.30', edgecolor = 'white')
      b2 = ax1.bar(ind+1, val[0,1], width, yerr=val[1,1], ecolor='k', color = '0.70', edgecolor = 'white')
      ax2.bar(ind, val[0,2], width, yerr=val[1,2], ecolor='k', color = '0.30', edgecolor = 'white')
      ax2.bar(ind+1, val[0,3], width, yerr=val[1,3], ecolor='k', color = '0.75', edgecolor = 'white')
      ind = ind+2
    ind = ind+2
    
  ax1.set_ylabel('HTER for Color')
  #ax1.set_title('Color Images')
  ax1.tick_params(axis='x', bottom='off', top='off')
  ax1.tick_params(axis='y', right='off', direction='out')
  ax1.set_xlim(-1,62)
  ax1.set_ylim(-9,55)
  ind = numpy.array([2,10,18,26,34,42,50,58])
  ax1.set_xticks(ind+width+0.5)
  ax1.set_xticklabels(['LBP(I)','LBP(B)','dLBP(I)','dLBP(B)','mLBP(I)','mLBP(B)','tLBP(I)','tLBP(B)'])
  ax1.axis["top"].line.set_visible(False)
  ax1.axis["top"].major_ticks.set_visible(False)
  ax1.axis["top"].major_ticklabels.set_visible(True)
  ax1.axis["top"].major_ticklabels.set_rotation(0)
  ax1.axis["top"].set_ticklabel_direction('+')
  ax1.axis["top"].major_ticklabels.set_pad(-5)
  #ax1.grid(axis='y')
  
  ax2.set_ylabel('HTER for Depth')
  #ax2.set_title('Depth Images')
  ax2.tick_params(axis='x', bottom='off', top='off')
  ax2.tick_params(axis='y', right='off', direction='out')
  ax2.set_xlim(-1,62)
  ax2.set_ylim(-5,30)
  ind = numpy.array([0,2,4,8,10,12,16,18,20,24,26,28,32,34,36,40,42,44,48,50,52,56,58,60])
  ax2.set_yticks([0,10,20,30])
  ax2.set_xticks(ind+width+0.5)
  ax2.set_xticklabels([r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA',r'$\chi^2$','SVM','LDA'])
  ax2.axis["bottom"].major_ticklabels.set_rotation(90)
  ax2.axis["bottom"].major_ticks.set_visible(False)
  ax2.axis["bottom"].line.set_visible(False)
  #l = ax2.legend((b1,b2),('Development Set','Test Set'),'upper right')
  #l.draw_frame(False)
  #ax2.grid(axis='y')
  
  file_name = os.path.join(path,'fig_performance.pdf')
  l = matplotlib.pyplot.figlegend((b1,b2),('Dev. Set','Test Set'),'center right')
  l.draw_frame(False)
  matplotlib.pyplot.savefig(file_name)
  
  return 0

if __name__ == "__main__":
  main()
