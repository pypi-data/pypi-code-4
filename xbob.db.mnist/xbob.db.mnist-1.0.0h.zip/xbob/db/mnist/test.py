#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the MNIST database.
"""

import unittest
from . import Database

class MNISTDatabaseTest(unittest.TestCase):
  """Performs various tests on the MNIST database."""

  def test01_query(self):
    db = Database()

    f = db.labels()
    self.assertEqual(len(f), 10) # number of labels (digits 0 to 9)
    for i in range(0,10):
      self.assertTrue(i in f)

    f = db.groups()
    self.assertEqual(len(f), 2) # Two groups
    self.assertTrue('train' in f)
    self.assertTrue('test' in f)

    # Test the number of samples/labels
    d, l = db.data(groups='train')
    self.assertEqual(d.shape[0], 60000)
    self.assertEqual(d.shape[1], 784)
    self.assertEqual(l.shape[0], 60000)
    d, l = db.data(groups='test')
    self.assertEqual(d.shape[0], 10000)
    self.assertEqual(d.shape[1], 784)
    self.assertEqual(l.shape[0], 10000)
    d, l = db.data()
    self.assertEqual(d.shape[0], 70000)
    self.assertEqual(d.shape[1], 784)
    self.assertEqual(l.shape[0], 70000)
