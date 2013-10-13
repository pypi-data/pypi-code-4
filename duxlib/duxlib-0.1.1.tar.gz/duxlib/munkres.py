from __future__ import absolute_import

import itertools

import munkres
import numpy as np
import pandas as pd


def match(left, right, cost):
  """Match objects according to a cost function

  Parameters
  ----------
  left : array-like
      objects to match on one side
  right : array-like
      objects to match on the other side
  cost : function
      two-arg function that assigns a cost to matching an element of `left`
      with an element of `right`.

  Returns
  -------
  matching : DataFrame
      A dataframe with `left`'s entries as its index and `right`'s as its
      columns. Entries are either 0 or 1 -- 1 indicating these two elements are
      matched in the minimum cost match, 0 indicating otherwise.
  """
  m = munkres.Munkres()

  # construct cost matrix
  left, right = list(left), list(right)
  n_left, n_right = len(left), len(right)
  costs = np.zeros([n_left, n_right])
  for i, j in itertools.product(range(n_left), range(n_right)):
    costs[i, j] = cost(left[i], right[j])

  # solve for lowest cost matching
  indices = m.compute(costs.tolist())

  # save and return
  result = pd.DataFrame(
      np.zeros([n_left, n_right]).tolist(),
      index=left,
      columns=right,
    )
  for i, j in indices:
    result.iloc[i, j] = 1

  return result


