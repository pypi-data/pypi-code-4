#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Nov 13 11:56:53 CET 2013
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

import os
import logging
logger = logging.getLogger("bob")

def read_annotation_file(file_name, annotation_type):
  """This function provides default functionality to read annotation files.
  It returns a dictionary with the keypoint name as key and the position (y,x) as value, and maybe some additional annotations.

  The following annotation_types are supported:

  * 'eyecenter': The file contains a single row with four entries: 're_x re_y le_x le_y'
  * 'named': The file contains named annotations, one per line, e.g.: 'reye re_x re_y'
  * 'idiap': The file contains enumerated annotations, one per line, e.g.: '1 key1_x key1_y', and maybe some additional annotations like gender, age, ...
  """

  if not file_name:
    return None

  if not os.path.exists(file_name):
    raise IOError("The annotation file '%s' was not found"%file_name)

  annotations = {}

  with open(file_name, 'r') as f:

    if str(annotation_type) == 'eyecenter':
      # only the eye positions are written, all are in the first row
      line = f.readline()
      positions = line.split()
      assert len(positions) == 4
      annotations['reye'] = (float(positions[1]),float(positions[0]))
      annotations['leye'] = (float(positions[3]),float(positions[2]))

    elif str(annotation_type) == 'named':
      # multiple lines, no header line, each line contains annotation and position
      for line in f:
        positions = line.split()
        assert len(positions) == 3
        annotations[positions[0]] = (float(positions[2]),float(positions[1]))

    elif str(annotation_type) == 'idiap':
      # multiple lines, no header, each line contains an integral keypoint identifier, or other identifier like 'gender', 'age',...
      for line in f:
        positions = line.rstrip().split()
        if positions:
          if positions[0].isdigit():
            # position field
            assert len(positions) == 3
            id = int(positions[0])
            annotations['key%d'%id] = (float(positions[2]),float(positions[1]))
          else:
            # keyword field
            assert len(positions) == 2
            annotations[positions[0]] = positions[1]

        # finally, we add the eye center coordinates as the center between the eye corners; the annotations 3 and 8 seem to be the pupils...
        if 'key1' in annotations and 'key5' in annotations:
          annotations['reye'] = ((annotations['key1'][0] + annotations['key5'][0])/2., (annotations['key1'][1] + annotations['key5'][1])/2.)
        if 'key6' in annotations and 'key10' in annotations:
          annotations['leye'] = ((annotations['key6'][0] + annotations['key10'][0])/2., (annotations['key6'][1] + annotations['key10'][1])/2.)

  if 'leye' in annotations and 'reye' in annotations and annotations['leye'][1] < annotations['reye'][1]:
    logger.warn("The eye annotations in file '%s' might be exchanged!" % file_name)

  return annotations
