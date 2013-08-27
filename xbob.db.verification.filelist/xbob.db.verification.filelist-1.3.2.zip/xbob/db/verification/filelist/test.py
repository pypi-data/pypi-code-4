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

"""A few checks at the Verification Filelist database.
"""

import os, sys
import unittest
from .query import Database

class VerificationFilelistTest(unittest.TestCase):
  """Performs various tests on the Verification Filelist database."""

  def test01_query(self):
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, '.')
    db = Database(os.path.join(example_data, 'example_fl'), use_dense_probe_file_list = False)

    self.assertEqual(len(db.client_ids()), 6) # 6 client ids for world, dev and eval
    self.assertEqual(len(db.client_ids(groups='world')), 2) # 2 client ids for world
    self.assertEqual(len(db.client_ids(groups='optional_world_1')), 2) # 2 client ids for optional world 1
    self.assertEqual(len(db.client_ids(groups='optional_world_2')), 2) # 2 client ids for optional world 2
    self.assertEqual(len(db.client_ids(groups='dev')), 2) # 2 client ids for dev
    self.assertEqual(len(db.client_ids(groups='eval')), 2) # 2 client ids for eval

    self.assertEqual(len(db.tclient_ids()), 2) # 2 client ids for T-Norm score normalization
    self.assertEqual(len(db.zclient_ids()), 2) # 2 client ids for Z-Norm score normalization

    self.assertEqual(len(db.model_ids()), 6) # 6 model ids for world, dev and eval
    self.assertEqual(len(db.model_ids(groups='world')), 2) # 2 model ids for world
    self.assertEqual(len(db.model_ids(groups='optional_world_1')), 2) # 2 model ids for optional world 1
    self.assertEqual(len(db.model_ids(groups='optional_world_2')), 2) # 2 model ids for optional world 2
    self.assertEqual(len(db.model_ids(groups='dev')), 2) # 2 model ids for dev
    self.assertEqual(len(db.model_ids(groups='eval')), 2) # 2 model ids for eval

    self.assertEqual(len(db.tmodel_ids()), 2) # 2 model ids for T-Norm score normalization

    self.assertEqual(len(db.objects(groups='world')), 8) # 8 samples in the world set

    self.assertEqual(len(db.objects(groups='dev', purposes='enrol')), 8) # 8 samples for enrollment in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='3')), 4) # 4 samples for to enroll model '3' in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='7')), 0) # 0 samples for enrolling model '7' (it is a T-Norm model)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe')), 8) # 8 samples as probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='client')), 8) # 8 samples as client probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='impostor')), 4) # 4 samples as impostor probes in the dev set

    self.assertEqual(len(db.tobjects(groups='dev')), 8) # 8 samples for enrolling T-norm models
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='7')), 4) # 4 samples for enrolling T-norm model '7'
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='3')), 0) # 0 samples for enrolling T-norm model '3' (no T-Norm model)
    self.assertEqual(len(db.zobjects(groups='dev')), 8) # 8 samples for Z-norm impostor accesses

    self.assertEqual(db.get_client_id_from_model_id('1'), '1')
    self.assertEqual(db.get_client_id_from_model_id('3'), '3')
    self.assertEqual(db.get_client_id_from_model_id('6'), '6')
    self.assertEqual(db.get_client_id_from_tmodel_id('7'), '7')


  def test02_query_protocol(self):
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, '.')
    db = Database(os.path.join(example_data), use_dense_probe_file_list = False)
    p = 'example_fl'

    self.assertEqual(len(db.client_ids(protocol=p)), 6) # 6 client ids for world, dev and eval
    self.assertEqual(len(db.client_ids(groups='world', protocol=p)), 2) # 2 client ids for world
    self.assertEqual(len(db.client_ids(groups='optional_world_1', protocol=p)), 2) # 2 client ids for optional world 1
    self.assertEqual(len(db.client_ids(groups='optional_world_2', protocol=p)), 2) # 2 client ids for optional world 2
    self.assertEqual(len(db.client_ids(groups='dev', protocol=p)), 2) # 2 client ids for dev
    self.assertEqual(len(db.client_ids(groups='eval', protocol=p)), 2) # 2 client ids for eval

    self.assertEqual(len(db.tclient_ids(protocol=p)), 2) # 2 client ids for T-Norm score normalization
    self.assertEqual(len(db.zclient_ids(protocol=p)), 2) # 2 client ids for Z-Norm score normalization

    self.assertEqual(len(db.model_ids(protocol=p)), 6) # 6 model ids for world, dev and eval
    self.assertEqual(len(db.model_ids(groups='world', protocol=p)), 2) # 2 model ids for world
    self.assertEqual(len(db.model_ids(groups='optional_world_1', protocol=p)), 2) # 2 model ids for optional world 1
    self.assertEqual(len(db.model_ids(groups='optional_world_2', protocol=p)), 2) # 2 model ids for optional world 2
    self.assertEqual(len(db.model_ids(groups='dev', protocol=p)), 2) # 2 model ids for dev
    self.assertEqual(len(db.model_ids(groups='eval', protocol=p)), 2) # 2 model ids for eval

    self.assertEqual(len(db.tmodel_ids(protocol=p)), 2) # 2 model ids for T-Norm score normalization

    self.assertEqual(len(db.objects(groups='world', protocol=p)), 8) # 8 samples in the world set

    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', protocol=p)), 8) # 8 samples for enrollment in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='3', protocol=p)), 4) # 4 samples for to enroll model '3' in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='enrol', model_ids='7', protocol=p)), 0) # 0 samples for enrolling model '7' (it is a T-Norm model)
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', protocol=p)), 8) # 8 samples as probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='client', protocol=p)), 8) # 8 samples as client probes in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe', classes='impostor', protocol=p)), 4) # 4 samples as impostor probes in the dev set

    self.assertEqual(len(db.tobjects(groups='dev', protocol=p)), 8) # 8 samples for enrolling T-norm models
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='7', protocol=p)), 4) # 4 samples for enrolling T-norm model '7'
    self.assertEqual(len(db.tobjects(groups='dev', model_ids='3', protocol=p)), 0) # 0 samples for enrolling T-norm model '3' (no T-Norm model)
    self.assertEqual(len(db.zobjects(groups='dev')), 8) # 8 samples for Z-norm impostor accesses

    self.assertEqual(db.get_client_id_from_model_id('1', protocol=p), '1')
    self.assertEqual(db.get_client_id_from_model_id('3', protocol=p), '3')
    self.assertEqual(db.get_client_id_from_model_id('6', protocol=p), '6')
    self.assertEqual(db.get_client_id_from_tmodel_id('7', protocol=p), '7')


  def test03_query_dense(self):
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, 'example_fl')
    db = Database(example_data, probes_filename = 'for_probes.lst')

    self.assertEqual(len(db.objects(groups='world')), 8) # 8 samples in the world set

    self.assertEqual(len(db.objects(groups='dev', purposes='enrol')), 8) # 8 samples for enrollment in the dev set
    self.assertEqual(len(db.objects(groups='dev', purposes='probe')), 8) # 8 samples as probes in the dev set


  def test04_driver_api(self):
    from bob.db.script.dbmanage import main
    from pkg_resources import resource_filename
    example_data = resource_filename(__name__, 'example_fl')
    self.assertEqual(main(('verification.filelist dumplist --list-directory=%s --self-test' % example_data).split()), 0)
    self.assertEqual(main(('verification.filelist dumplist --list-directory=%s --purpose=enrol --group=dev --class=client --self-test' % example_data).split()), 0)
    self.assertEqual(main(('verification.filelist checkfiles --list-directory=%s --self-test' % example_data).split()), 0)


