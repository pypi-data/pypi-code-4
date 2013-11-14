#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Nov 13 12:46:06 CET 2013
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

import unittest
from bob.test.utils import datafile
import xbob.db.verification.utils

class VerificationUtilsTest (unittest.TestCase):
  def test01_annotations(self):
    # tests the annotation IO functionality provided by this utility class

    # check the different annotation types
    for annotation_type in ('eyecenter', 'named', 'idiap'):
      # get the annotation file name
      annotation_file = datafile("%s.pos" % annotation_type, 'xbob.db.verification.utils', 'test_files')
      # read the annotations
      annotations = xbob.db.verification.utils.read_annotation_file(annotation_file, annotation_type)
      # check
      self.assertTrue('leye' in annotations)
      self.assertTrue('reye' in annotations)
      self.assertEqual(annotations['leye'], (20,40))
      self.assertEqual(annotations['reye'], (20,10))

