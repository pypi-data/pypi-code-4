from __future__ import absolute_import

def merge(*dicts):
  """Merge dictionaries together, with earlier dicts taking preference"""
  result = {}
  for d in reversed(dicts):
    result.update(d)
  return result
