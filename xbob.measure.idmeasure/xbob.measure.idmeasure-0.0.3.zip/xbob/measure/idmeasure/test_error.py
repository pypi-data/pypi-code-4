#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed Apr 20 17:32:54 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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

"""Basic tests for the error measuring system of bob
"""

import os, sys
import unittest
import numpy
import bob
#import pkg_resources

from . import idmeasure
def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

def count(array, value=True):
  """Counts occurrences of a certain value in an array"""
  return list(array == value).count(True)

def save(fname, data):
  """Saves a single array into a file in the 'data' directory."""
  bob.io.Array(data).save(os.path.join('data', fname))

class ErrorTest(unittest.TestCase):
  """Various measure package tests for error evaluation."""

  def test_DIR(self):
    # tests the DIR calculation
    # test data; should give match characteristics [1/2,1/4,1/3] and CMC [1/3,2/3,1]
    cmc_scores=bob.measure.load.cmc_four_column('./docs/scores.txt')
#    test_data = [((0.3, 1.1, 0.5), (0.7)), ((1.4, -1.3, 0.6), (0.2)), ((0.8, 0., 1.5), (-0.8,1.8)), ((2., 1.3, 1.6, 0.9), (2.4))]
    # compute recognition rate
    rr = bob.measure.recognition_rate(cmc_scores)
    self.assertEqual(rr, 0.84)
    # compute CMC
    FAR=[.01, 0.1, 1]
    out =  idmeasure.DIR(cmc_scores, FAR)
    self.assertTrue((out[0][0] == [0.84,0.96,0.99,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.]).all())
    self.assertTrue((out[1][0] == [0.84,0.92,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,0.94,1.]).all())
    self.assertTrue((out[2][0] == [0.79,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,0.82,1. ]).all())

