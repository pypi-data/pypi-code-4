#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon Aug 8 12:40:24 2011 +0200
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

"""A few checks at the replay attack database.
"""

import os, sys
import unittest
from .query import Database
from .models import *

class MaskAttackDatabaseTest(unittest.TestCase):
  """Performs various tests on the 3d mask attack database."""

  def test01_queryVerificationProtocol(self):
  
    db = Database()
    f = db.objects(protocol='verification')
    self.assertEqual(len(f), 220) #220 files to be used in verification excluding mask attacks for the training subjects (255-(7*5))
    f = db.objects(protocol='verification',sets='world')
    self.assertEqual(len(f), 70) #7*10
    f = db.objects(protocol='verification',sets='dev')
    self.assertEqual(len(f), 75) #5*15
    f = db.objects(protocol='verification',sets='test')
    self.assertEqual(len(f), 75) #5*15
    f = db.objects(protocol='verification',sets='world',purposes='trainReal')
    self.assertEqual(len(f), 70) #7*10
    f = db.objects(protocol='verification',sets='dev',purposes='enrol')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='verification',sets='dev',purposes='probeReal')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='verification',sets='dev',purposes='probeMask')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='verification',sets='test',purposes='enrol')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='verification',sets='test',purposes='probeReal')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='verification',sets='test',purposes='probeMask')
    self.assertEqual(len(f), 25) #5*5
  
  def test02_queryClassificationProtocol(self):
  
    db = Database()
    f = db.objects(protocol='classification')
    self.assertEqual(len(f), 255) #All files
    f = db.objects(protocol='classification',sets='world')
    self.assertEqual(len(f), 105) #7*15
    f = db.objects(protocol='classification',sets='dev')
    self.assertEqual(len(f), 75) #5*15
    f = db.objects(protocol='classification',sets='test')
    self.assertEqual(len(f), 75) #5*15
    f = db.objects(protocol='classification',sets='world',purposes='trainReal')
    self.assertEqual(len(f), 70) #7*10
    f = db.objects(protocol='classification',sets='world',purposes='trainMask')
    self.assertEqual(len(f), 35) #7*5
    f = db.objects(protocol='classification',sets='dev',purposes='classifyReal')
    self.assertEqual(len(f), 50) #5*10
    f = db.objects(protocol='classification',sets='dev',purposes='classifyMask')
    self.assertEqual(len(f), 25) #5*5
    f = db.objects(protocol='classification',sets='test',purposes='classifyReal')
    self.assertEqual(len(f), 50) #5*10
    f = db.objects(protocol='classification',sets='test',purposes='classifyMask')
    self.assertEqual(len(f), 25) #5*5
  
  def test03_queryClients(self):

    db = Database()
    f = db.clients()
    self.assertEqual(len(f), 17) #17 clients
    self.assertTrue(db.has_client_id(1))
    self.assertFalse(db.has_client_id(0))
    self.assertTrue(db.has_client_id(8))
    self.assertFalse(db.has_client_id(18))
    self.assertFalse(db.has_client_id(20))
    self.assertTrue(db.has_client_id(9))
    self.assertTrue(db.has_client_id(16))
    self.assertFalse(db.has_client_id(25))

  def test04_manage_dumplist_1(self):

    from bob.db.script.dbmanage import main

    self.assertEqual(main('maskattack dumplist --self-test'.split()), 0)

  def test05_manage_dumplist_2(self):
    
    from bob.db.script.dbmanage import main

    self.assertEqual(main('maskattack dumplist --class=attack --group=devel --support=hand --protocol=highdef --self-test'.split()), 0)

  def test06_manage_dumplist_client(self):
    
    from bob.db.script.dbmanage import main

    self.assertEqual(main('maskattack dumplist --client=11 --self-test'.split()), 0)

  def test07_manage_checkfiles(self):

    from bob.db.script.dbmanage import main

    self.assertEqual(main('maskattack checkfiles --self-test'.split()), 0)
