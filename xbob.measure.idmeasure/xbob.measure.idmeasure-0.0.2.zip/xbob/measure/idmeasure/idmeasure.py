#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Chi Ho CHAN <c.chan@surrey.ac.uk>
# @date: Mon July  8 11:33:00 CEST 2013
#
# Copyright (C) 2011-2013 CVSSP, University of Surrey, U.K.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bob
import os, sys
import numpy

def DIR(cmc_scores, far_list):
  pos_scores =numpy.array([], dtype=numpy.float64)
  neg_scores =numpy.array([], dtype=numpy.float64)
  for neg,pos in cmc_scores:
      pos_scores=numpy.concatenate((pos_scores,pos))
      neg_scores=numpy.concatenate((neg_scores,neg))

  sorted_far_list=sorted(far_list, reverse=True)
  far_thres_list=[]
  for far in sorted_far_list:	
    far_thres_list.append((numpy.array(far, numpy.float64),numpy.array(bob.measure.far_threshold(neg_scores,pos_scores,far), numpy.float64)))

  retval = []
  cmc_scores1=cmc_scores
  for far, thres in far_thres_list:
    for neg, pos in cmc_scores1:
      pos[pos<thres]=thres-.01
      neg[neg<thres]=thres
    retval.append((numpy.array(bob.measure.cmc(cmc_scores1),numpy.float64), far))

  return retval

def DIR_plot(cmc_scores, far_list, logx = True, **kwargs):
  try:
    import matplotlib.pyplot as mpl
  except ImportError:
    print("Cannot import matplotlib. This package is not essential, but required if you wish to use the plotting functionality.")
    raise
  out =  DIR(cmc_scores, far_list)

  for cmc,far in out:
    if logx:
      mpl.semilogx(range(1, len(cmc)+1), cmc*100, label='$FAR = %f$' %far)
    else:
      mpl.plot(range(1, len(cmc)+1), cmc*100, label='$FAR = %f$' %far)
  mpl.legend()

