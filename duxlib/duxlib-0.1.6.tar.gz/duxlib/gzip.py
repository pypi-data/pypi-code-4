from __future__ import absolute_import

import gzip
from StringIO import StringIO


def encode(s):
  """Encode a string with gzip"""
  sio = StringIO()
  gz = gzip.GzipFile(fileobj=sio, mode='w')
  gz.write(s)
  gz.close()
  return sio.getvalue()


def decode(s):
  """Decode a gzip-encoded string"""
  gz = gzip.GzipFile(fileobj=StringIO(s), mode='r')
  return gz.read()
