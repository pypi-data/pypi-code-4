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

"""A few checks
"""

import os, sys
import unittest
import tempfile, shutil

class PaperTest(unittest.TestCase):
  """Performs various tests."""

  def test01_scripts(self):
    """Tests the four scripts"""

    # Create a temporary directory
    test_dir = tempfile.mkdtemp(prefix='aetest_')

    # L-BFGS script
    from xbob.paper.jmlr2013.scripts.lbfgs_training import main as lbfgs
    parameters_lbfgs = [
        '-m', os.path.join(test_dir, 'lbfgs.hdf5'),
        '-H', '0',
        '-I', '1'
    ]
    self.assertEqual(lbfgs([sys.argv[0]] + parameters_lbfgs), 0)

    # R-prop script
    from xbob.paper.jmlr2013.scripts.rprop_training import main as rprop
    parameters_rprop = [
        '-m', os.path.join(test_dir, 'rprop.hdf5'),
        '-H', '0',
        '-I', '1'
    ]
    self.assertEqual(rprop([sys.argv[0]] + parameters_rprop), 0)

    # evaluate script
    from xbob.paper.jmlr2013.scripts.evaluate import main as evaluate
    parameters_eval = [
        '-m', os.path.join(test_dir, 'lbfgs.hdf5'),
    ]
    self.assertEqual(evaluate([sys.argv[0]] + parameters_eval), 0)

    # plot script
    from xbob.paper.jmlr2013.scripts.plot import main as plt
    parameters_plot = [
        '-m', os.path.join(test_dir, 'lbfgs.hdf5'), os.path.join(test_dir, 'rprop.hdf5'),
        '-l', 'lbfgs', 'rprop'
    ]
    self.assertEqual(plt([sys.argv[0]] + parameters_plot), 0)

    # Clean up
    shutil.rmtree(test_dir)
