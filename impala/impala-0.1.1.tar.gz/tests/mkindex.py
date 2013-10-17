# vim: sw=2 sts=2 et fdm=indent

import __future__
import os
import sys

from impalatest import find_tests

docwidth = 70

def hdelim(c):
  print(docwidth * c)

def doctitle(title):
  print(title.center(docwidth))

testdir = os.path.dirname(sys.argv[0]) or '.'

title = 'impala tests'

if __name__ == '__main__':
  print(testdir)
  print(find_tests(testdir))

  hdelim('=')
  doctitle(title)
  hdelim('=')
  print()

