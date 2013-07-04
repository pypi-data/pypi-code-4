#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 01 Mar 2013 13:07:55 CET

"""Methods for loading data and window with overlap at the same time.
"""

import numpy
import scipy.stats

def load(obj, inputdir, window_size, overlap, skip):
  """Loads the data from the filename given, applying the windowing operation
  if necessary.

  Keyword parameters:

  obj
    This is the File object loaded from the anti-spoofing database

  inputdir
    The input directory that contains the features to be loaded

  window_size
    The overall window-size to be considered for the calculation

  overlap
    The overlap between different windows

  skip
    The number of frames to skip between scores. If you set this to zero, than
    all scores are considered. If you set it to 1, only half. To 2, 1/3, and so
    on. This flag allows you to evaluate the expected degradation when
    skipping frames. Effectively, it is implemented by replacing selected parts
    of the loaded data with NaNs.

  Returns a 1D numpy.ndarray with all scores related to the given database file
  object, averaged according to your window-size, overlap and skip parameters.
  """

  data = obj.load(inputdir, '.hdf5')
  if skip:
    idx = [k for k in range(data.size) if k not in range(0,data.size,skip+1)]
    data[idx] = numpy.nan
  if window_size is not None:
    data = numpy.nan_to_num(data)
    N = len(data)
    start_range = range(0, N-window_size+1, window_size-overlap)
    end_range = range(window_size, N+1, window_size-overlap)
    indices = zip(start_range, end_range)
    retval = numpy.ndarray((len(indices),), dtype='float64')
    for k, (start, end) in enumerate(indices):
      retval[k] = scipy.stats.nanmean(data[start:end])
    return retval
  return data.flat
