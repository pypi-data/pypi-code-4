#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'yarnaid'

import unittest
import os

import glespy.test_data.data as test_data
import glespy.tools.convertion as convert
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
        attrs = convert.get_map_attrs(map_name=self.map_name)
        self.assertEqual(self.attrs, attrs)

    def test_map_to_alm_good(self):
        """
        check of map convert to alm
        """
        alm_from_map = os.path.join(self.data_path, 'alm_test.fit')
        alm = convert.map_to_alm(
            map_name=self.map_name, alm_name=alm_from_map)
        self.check_existance(alm_from_map)
        os.remove(alm_from_map)

    def test_map_to_alm_no_alm(self):
        """
        check of map convert to alm
        """
        alm_name = convert.map_to_alm(map_name=self.map_name)
        self.check_existance(alm_name)
        os.remove(alm_name)

    # @unittest.skip('too long')
    def test_map_to_gif_no_gif(self):
        gif_name = convert.map_to_gif(self.map_name)
        self.check_existance(gif_name)
        os.remove(gif_name)

    @unittest.skip('Not important test')
    def test_show_map(self):
        convert.show_map(self.map_name)

    def test_kwargs_to_glesp_2(self):
        d = {'lmax': '10', 'n': 'str'}
        l = ['-lmax', '10', '-n', 'str'].sort()
        self.assertEqual(convert.kwargs_to_glesp_args(**d).sort(), l)

    def test_alm_to_map_with_lmax(self):
        mp = convert.alm_to_map(self.alm_100_name, lmax=100)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_with_l(self):
        mp = convert.alm_to_map(self.alm_100_name, l=33)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_with_nx(self):
        mp = convert.alm_to_map(self.alm_100_name, nx=123)
        self.check_existance(mp)
        os.remove(mp)

    def test_alm_to_map_with_np(self):
        mp = convert.alm_to_map(self.alm_100_name, np=231)
        self.check_existance(mp)
        os.remove(mp)

    def test_map_to_hist_with_name_and_hn(self):
        hist = convert.map_to_hist(self.map_name, hn=20)
        self.assertEqual(len(hist), 20)
        self.assertEqual(len(hist[-1]), 2)

    # @unittest.skip('very long...')
    def test_mask_map_without_name(self):
        masked = convert.mask_map(self.map_name, mask_name=self.mask_name)
        self.check_existance(masked)
        os.remove(masked)

    def test_points_to_map_without_name_with_error(self):
        self.assertRaises(
            ValueError, convert.points_to_map,
            points_name=self.points_name)

    def test_points_to_map_without_name(self):
        points_map = convert.points_to_map(self.points_name, nx=201)
        self.check_existance(points_map)
        os.remove(points_map)

    def test_smooth_alm_without_name(self):
        smoothed = convert.smooth_alm(self.alm_100_name, 300)
        self.check_existance(smoothed)
        os.remove(smoothed)

    def test_correlate(self):
        correlated_map = convert.correlate(self.map_name,
                                           convert.points_to_map(
                                           self.points_name,
                                           **self.attrs),
                                           180)
        self.check_existance(correlated_map)
        os.remove(correlated_map)

    def test_sum_maps(self):
        m1 = convert.points_to_map(self.points_name, **self.attrs)
        m2 = self.map_name
        sum = convert.sum_map(m1, m2)
        self.check_exist(sum)

    def test_rotate_alm(self):
        rotated = convert.rotate_alm(
            alm_name=self.alm_100_name, dphi=2, dtheta=2)
        self.check_existance(rotated)
        os.remove(rotated)

    def test_cut_map_circle(self):
        cutted = convert.cut_map_zone(self.map_name, angles.Zone(90, 0))
        self.check_existance(cutted)

    def test_alm_rotate_with_angle(self):
        rotated = convert.rotate_alm(
            self.alm_100_name,
            angle=angles.Angle(10, 100)
        )
        self.check_existance(rotated)

    def test_reflaction(self):
        r_map = convert.reflect_map(
            map_name=self.map_name,
            rtype='h'
        )
        self.check_existance(r_map)

    def test_mult(self):
        mult = convert.mult_map(
            self.map_name,
            mult=-1000,
        )
        self.check_existance(mult)
