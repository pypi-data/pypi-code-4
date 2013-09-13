# -*- coding: utf-8 -*-
__author__ = 'yarnaid'
try:
    import glespy.pointsource as pointsource
    import glespy.test_data.data as data
    # import glespy.pixelmap as pixelmap
except:
    import pointsource
    import test_data.data as data
    # import pixelmap

import unittest


class PointSourceTest(unittest.TestCase, data.WithTestData):

    def setUp(self):
        super(PointSourceTest, self).setUp()
        self.init_data()

    def test_to_pixelmap_with_nx(self):
        psource = pointsource.PointSource(name=self.points_name)
        p_map = psource.to_pixelmap(nx=101)
        self.check_exist(p_map.name)
