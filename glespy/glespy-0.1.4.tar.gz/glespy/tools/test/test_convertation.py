__author__ = 'yarnaid'

import unittest
import os

try:
    import tools.convertion as convertation
    import test_data.data as test_data
    import ext.angles as angles
except:
    import glespy.test_data.data as test_data
    import glespy.tools.convertion as convertation
    import glespy.ext.angles as angles


class FunctionsTests(unittest.TestCase, test_data.WithTestData):

    def setUp(self):
        self.init_data()
        print(self.alm_100_name)
        self.check_existance(self.alm_100_name)
        self.check_existance(self.map_name)

    def check_existance(self, file_name):
        self.assertTrue(os.path.exists(file_name))
        self.assertGreater(os.path.getsize(file_name), 0)

    def test_get_map_attrs(self):
        """
        check getting attributes of map
        """
        attrs = convertation.get_map_attrs(map_name=self.map_name)
        self.assertEqual(self.attrs, attrs)

    def test_map_to_alm_good(self):
        """
        check of map convertation to alm
        """
        alm_from_map = os.path.join(self.data_path, 'alm_test.fit')
        alm = convertation.map_to_alm(
            map_name=self.map_name, alm_name=alm_from_map)
        self.check_existance(alm_from_map)
        os.remove(alm_from_map)

    def test_map_to_alm_no_alm(self):
        """
        check of map convertation to alm
        """
        alm_name, lmax = convertation.map_to_alm(map_name=self.map_name)
        self.check_existance(alm_name)
        os.remove(alm_name)

    # @unittest.skip('too long')
    def test_map_to_gif_no_gif(self):
        gif_name = convertation.map_to_gif(self.map_name)
        self.check_existance(gif_name)
        os.remove(gif_name)

    @unittest.skip('Not important test')
    def test_show_map(self):
        convertation.show_map(self.map_name)

    def test_kwargs_to_glesp_2(self):
        d = {'lmax': '10', 'n': 'str'}
        l = ['-lmax', '10', '-n', 'str'].sort()
        self.assertEqual(convertation.kwargs_to_glesp_args(**d).sort(), l)

    def test_alm_to_map_with_lmax(self):
        mp = convertation.alm_to_map(self.alm_100_name, lmax=100)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_without_params(self):
        self.assertRaises(
            ValueError, convertation.alm_to_map, {'map_name': self.alm_100_name})

    def test_alm_to_map_with_l(self):
        mp = convertation.alm_to_map(self.alm_100_name, l=33)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_with_nx(self):
        mp = convertation.alm_to_map(self.alm_100_name, nx=123)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_with_np(self):
        mp = convertation.alm_to_map(self.alm_100_name, np=231)
        self.check_existance(mp)
        os.remove(mp)

    def test_map_to_hist_with_name_and_hn(self):
        hist = convertation.map_to_hist(self.map_name, hn=20)
        self.assertEqual(len(hist), 20)
        self.assertEqual(len(hist[-1]), 2)

    # @unittest.skip('very long...')
    def test_mask_map_without_name(self):
        masked = convertation.mask_map(self.map_name, mask_name=self.mask_name)
        self.check_existance(masked)
        os.remove(masked)

    def test_points_to_map_without_name_with_error(self):
        self.assertRaises(
            ValueError, convertation.points_to_map,
            points_name=self.points_name)

    def test_points_to_map_without_name(self):
        points_map = convertation.points_to_map(self.points_name, nx=201)
        self.check_existance(points_map)
        os.remove(points_map)

    def test_smooth_alm_without_name(self):
        smoothed = convertation.smooth_alm(self.alm_100_name, 300)
        self.check_existance(smoothed)
        os.remove(smoothed)

    def test_correlate(self):
        correlated_map = convertation.correlate(self.map_name,
                                                convertation.points_to_map(
                                                    self.points_name,
                                                    **self.attrs),
                                                180)
        self.check_existance(correlated_map)
        os.remove(correlated_map)

    def test_sum_maps(self):
        m1 = convertation.points_to_map(self.points_name, **self.attrs)
        m2 = self.map_name
        sum = convertation.sum_map(m1, m2)
        self.check_exist(sum)

    def test_rotate_alm(self):
        rotated = convertation.rotate_alm(
            alm_name=self.alm_100_name, dphi=2, dtheta=2)
        self.check_existance(rotated)
        os.remove(rotated)

    def test_cut_map_circle(self):
        cutted = convertation.cut_map_zone(self.map_name, angles.Zone(90, 0))
        self.check_existance(cutted)
