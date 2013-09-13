import os
import error_utils

def ensure_dir(f):
  """Creates the directory for the filename given as an argument, if it does not exist"""
  d = os.path.dirname(f)
  if not os.path.exists(d):
    os.makedirs(d)
