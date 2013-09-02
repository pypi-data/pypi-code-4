#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Apr 15 18:44:13 CEST 2013
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

import sys
import os
import subprocess
import pkg_resources

def main():
  patch_file = pkg_resources.resource_filename(__name__, 'facereclib.patch')
  setup_file = pkg_resources.resource_filename(__name__, 'setup.py.patch')

  if len(sys.argv) < 2:
    raise ValueError, "Please specify the directory to be patched."


  if not os.path.isdir(sys.argv[1]):
    raise ValueError, "The given directory '%s' does not exist." % sys.argv[1]


  base_dir = os.path.join(sys.argv[1], 'PythonFaceEvaluation')
  if not os.path.isdir(base_dir):
    raise IOError, "The given directory '%s' does not contain a 'PythonFaceEvaluation' subdirectory. Please specify the base directory of the PythonFaceEvaluation toolkit." % sys.argv[1]

  if os.path.isfile(os.path.join(base_dir, 'setup.py')):
    raise IOError, "The given directory '%s' already seems to be patched." % sys.argv[1]

  os.chdir(base_dir)
  subprocess.call(['patch', '-bp1', '-i', patch_file, '--verbose'])

