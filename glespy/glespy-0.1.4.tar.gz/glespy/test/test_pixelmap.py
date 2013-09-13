__author__ = 'yarnaid'

import unittest
try:
    import pixelmap
    import test_data.data as data
    import pointsource
except:
    import glespy.pixelmap as pixelmap
    import glespy.test_data.data as data
    import glespy.pointsource as pointsource


class PixelMapTests(unittest.TestCase, data.WithTestData):


    def setUp(self):
        super(PixelMapTests, self).setUp()
        self.init_data()


    def check_params_with_lmax(self, pm, lmax):
        self.assertEqual(pm.lmax, 100)
        self.assertGreaterEqual(pm.lmax, pm.lmin)
        self.assertGreaterEqual(pm.nx, pm.lmax * 2 + 1)
        self.assertGreaterEqual(pm.np, pm.nx * 2)

    def test_creation(self):
        pm = pixelmap.gPixelMap(lmax=100)
        self.check_params_with_lmax(pm, 100)

    @unittest.expectedFailure
    def test_from_alm(self):
        self.check_exist('alm')

    def test_sum_with_ps(self):
        pm = pixelmap.gPixelMap(name=self.map_name, **self.attrs)
        ps = pointsource.PointSource(name=self.points_name).to_pixelmap(**self.attrs)
        pm.add_map(ps)
        self.check_exist(pm.name)
