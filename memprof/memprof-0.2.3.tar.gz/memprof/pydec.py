#!/usr/bin/env python
from functools import wraps, update_wrapper
import timeit
import os
import sys

def decorator(d):
  "Make function d a decorator: d wraps a function fn."
  def _d(fn):
    return update_wrapper(d(fn), fn)
  update_wrapper(_d, d)
  return _d

@decorator
def memo(f):
  """Decorator that caches the return value for each call to f(args).
  Then when called again with same args, we can just look it up."""
  cache = {}
  def _f(*args):
    try:
      return cache[args]
    except KeyError:
      cache[args] = result = f(*args)
      return result
    except TypeError:
      # some element of args can't be a dict key
      return f(args)
  return _f


def logging(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    res = func(*args, **kwargs)
    print '%s %s %s returned %s' % (func.__name__, args, kwargs,res)
    return res
    
  return wrapper

def timing(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    t = timeit.default_timer()
    res = func(*args, **kwargs)
    print '%s: %f seconds' % (func.__name__, timeit.default_timer()-t)
    return res
    
  return wrapper

# number, repeat
def benchmarking(n=1,r=1):
  def mybench(func):  
    @wraps(func)
    def wrapper(*args, **kwargs):
      if 'leavemealone' not in kwargs or not kwargs['leavemealone']:
        kwargs['leavemealone']=True
        print 'repeat=%d\tnumber=%d' % (r,n)
        
        theArgs = ','.join(["'%s'" % a for a in args])
        theKwargs = ','.join(["%s='%s'" % (k,v) for k,v in kwargs.items()])
        
        f = open(os.devnull, 'w')
        
        tmp_stdout,sys.stdout = sys.stdout,f
        tmp_stderr,sys.stderr = sys.stderr,f
              
        res = timeit.repeat("%s(%s%s%s)" % (func.__name__,theArgs,',' if theArgs else '',theKwargs), setup="from __main__ import %s" % func.__name__, repeat = r, number = n)
        
        sys.stdout = tmp_stdout
        sys.stderr = tmp_stderr
        
        f.close()
        
        print '%s: %s seconds' % (func.__name__, res)
      else:
        del kwargs['leavemealone']
        res = func(*args, **kwargs)
      
      return res
          
    return wrapper
    
  return mybench

