from __future__ import absolute_import

import datetime
import json


__all__ = [
  'escape'
]

def _escape_list(o):
  return [ escape(e) for e in o ]


def _escape_dict(o):
  result = {}
  for k, v in o.items():
    result[k] = escape(v)
  return result


def _escape_datetime(o):
  return o.isoformat()


def _escape_string(o):
  try:
    json.dumps(o)
    return o
  except UnicodeDecodeError:
    # handle unicode encoding errors
    return o.decode("utf8", errors="replace")



# functions for escaping json
ESCAPE_FUNCTIONS = [
  (lambda x: isinstance(x, list)             , _escape_list),
  (lambda x: isinstance(x, tuple)            , _escape_list),
  (lambda x: isinstance(x, dict)             , _escape_dict),
  (lambda x: isinstance(x, datetime.datetime), _escape_datetime),
  (lambda x: isinstance(x, datetime.date)    , _escape_datetime),
  (lambda x: isinstance(x, basestring)       , _escape_string),
  (lambda x: hasattr(x, '__iter__')          , _escape_list),
]


def escape(o):
  """Escape an object such that `json.dump` works on it"""
  for (test, escaper) in ESCAPE_FUNCTIONS:
    if test(o):
      return escaper(o)
  return o
