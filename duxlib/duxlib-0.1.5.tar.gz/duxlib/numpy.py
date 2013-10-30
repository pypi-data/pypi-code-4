from __future__ import absolute_import

import numpy as np


def inner(arr, p, sorted=False):
  """Get mask for points in `arr` that form the inner `p` percentage of points when sorted"""
  arr = np.asarray(arr)
  sorted = np.sort(arr)
  p = 1-p
  p_low, p_high = 100 * p/2.0, 100 * (1-p/2.0)
  lower, upper = scoreatpercentile(sorted, [p_low, p_high])
  return (arr >= lower) & (arr <= upper)


def scoreatpercentile(a, per, limit=(), interpolation_method='fraction',
    axis=None):
  """Extracted from scipy.stats; because loading all of scipy just for this is stupid. """
  def _compute_qth_percentile(sorted, per, interpolation_method, axis):
    if not np.isscalar(per):
      return [_compute_qth_percentile(sorted, i, interpolation_method, axis)
         for i in per]

    if (per < 0) or (per > 100):
      raise ValueError("percentile must be in the range [0, 100]")

    indexer = [slice(None)] * sorted.ndim
    idx = per / 100. * (sorted.shape[axis] - 1)

    if int(idx) != idx:
      # round fractional indices according to interpolation method
      if interpolation_method == 'lower':
        idx = int(np.floor(idx))
      elif interpolation_method == 'higher':
        idx = int(np.ceil(idx))
      elif interpolation_method == 'fraction':
        pass  # keep idx as fraction and interpolate
      else:
        raise ValueError("interpolation_method can only be 'fraction', "
                 "'lower' or 'higher'")

    i = int(idx)
    if i == idx:
      indexer[axis] = slice(i, i + 1)
      weights = np.array(1)
      sumval = 1.0
    else:
      indexer[axis] = slice(i, i + 2)
      j = i + 1
      weights = np.array([(j - idx), (idx - i)], float)
      wshape = [1] * sorted.ndim
      wshape[axis] = 2
      weights.shape = wshape
      sumval = weights.sum()

    # Use np.add.reduce to coerce data type
    return np.add.reduce(sorted[indexer] * weights, axis=axis) / sumval

  a = np.asarray(a)

  if limit:
    a = a[(limit[0] <= a) & (a <= limit[1])]

  if per == 0:
    return a.min(axis=axis)
  elif per == 100:
    return a.max(axis=axis)

  sorted = np.sort(a, axis=axis)
  if axis is None:
    axis = 0

  return _compute_qth_percentile(sorted, per, interpolation_method, axis)


