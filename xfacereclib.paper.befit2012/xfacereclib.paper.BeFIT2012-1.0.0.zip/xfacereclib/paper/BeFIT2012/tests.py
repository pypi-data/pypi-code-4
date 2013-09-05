#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Tue Jul  2 20:01:21 CEST 2013
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
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


import facereclib

# Here we test all installed databases and everything else that has a bob.test declared in the setup.py
# The technology is adapted from the xbob.db.aggregator tests
import pkg_resources
for i, ep in enumerate(pkg_resources.iter_entry_points('bob.test')):
  ep_parts = str(ep).split(' = ')[1].split(':')
  facereclib.utils.debug("Collected test '%s' from '%s'"% (ep_parts[1], ep_parts[0]))
  cls = ep.load()
  exec('Test%d = cls' % i)
  exec('Test%d.__name__ = "%s [%s:%s]"' % (i, ep_parts[1], ep_parts[0], ep_parts[1]))

# clean-up since otherwise the last test is re-run
del cls


import unittest
import tempfile
import os
import shutil

class BeFIT2012Test(unittest.TestCase):

  def test01_execute(self):
    # Test the interface of the execute script
    from xfacereclib.paper.BeFIT2012.execute import main
    test_dir = tempfile.mkdtemp(prefix='xfrltest_')
    main(['--temp-directory', test_dir, '--result-directory', test_dir, '--dry-run'])
    main(['--temp-directory', test_dir, '--result-directory', test_dir, '--', '--dry-run'])
    try:
      import gridtk
      main(['--temp-directory', test_dir, '--result-directory', test_dir, '--grid', '--', '--dry-run'])
      main(['--temp-directory', test_dir, '--result-directory', test_dir, '--local', '--', '--dry-run'])
    except ImportError:
      pass

    # clean up the mess that we created
    if os.path.exists(test_dir):
      shutil.rmtree(test_dir)



  def test02_evaluate(self):
    from xfacereclib.paper.BeFIT2012.evaluate import main
    test_dir = tempfile.mkdtemp(prefix='xfrltest_')

    # test banca
    try:
      os.mkdir(os.path.join(test_dir, 'BANCA'))
      main(['--result-dir', test_dir, '--databases', 'BANCA'])
    except IOError:
      os.rmdir(os.path.join(test_dir, 'BANCA'))

    # test gbu
    try:
      os.mkdir(os.path.join(test_dir, 'GBU'))
      main(['--result-dir', test_dir, '--databases', 'GBU', '--gbu-plot-file', os.path.join(test_dir, 'plot.pdf')])
    except IOError:
      os.rmdir(os.path.join(test_dir, 'GBU'))

    shutil.rmtree(test_dir)


