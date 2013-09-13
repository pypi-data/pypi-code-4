import os

__author__ = 'yarnaid'

import unittest
try:
    import test_data.data as Data
    import alm as Alm
except:
    import glespy.test_data.data as Data
    import glespy.alm as Alm


class AlmTests(unittest.TestCase, Data.WithTestData):


    def setUp(self):
        super(AlmTests, self).setUp()
        self.init_data()
        self.check_exist(self.alm_100_name)

    def check_exist(self, name):
        self.assertTrue(os.path.exists(name))
        self.assertGreater(os.path.getsize(name), 0)

    def test_to_map(self):
        alm = Alm.Alm(name=self.alm_100_name, lmax=100)
        pmap = alm.to_map(nx=30)
        self.check_exist(pmap.name)
        os.remove(pmap.name)
