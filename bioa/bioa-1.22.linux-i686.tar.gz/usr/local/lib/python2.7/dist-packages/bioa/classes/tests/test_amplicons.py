#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nose.tools import *
import bioa

class TestAmplicons(object):

    def test_build_amplicons(self):
        data = []
        se_pos = []
        # empty amplicons should raise an exception
        #assert_raises(ValueError, bioa.Amplicons, data, se_pos, 0, 0)

        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        # should built just fine
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        for amplicon in amplicons:
            for read in amplicon:
                eq_(len(read), 4, "read length is not 4!")

        data = [("abab", 0), ("aabb", 0),
                ("baaa", 7), ("baba", 7)]
        se_pos = [(0, 4), (3, 7)]
        # empty amplicons -anywhere- should raise an exception
        #assert_raises(ValueError, bioa.Amplicons, data, se_pos, 0, 7)

    def test_build_uniform_amplicons(self):
        data = []
        # empty amplicons should raise an exception
        #assert_raises(ValueError, bioa.Amplicons.build_uniform_amplicons, data, 0, 0, 0)
        #assert_raises(ValueError, bioa.Amplicons.build_uniform_amplicons, data, 2, 0, 0)
        #assert_raises(ValueError, bioa.Amplicons.build_uniform_amplicons, data, 2, 1, 0)

        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        amplicons = bioa.Amplicons.build_uniform_amplicons(data, 4, 1, 7)
        for amplicon in amplicons:
            for read in amplicon:
                eq_(len(read), 4, "read length is not 4!")

        # more cases with reads being cleaned out
        data = [("abbb", 0), ("aabb", 0), ("bbba", 0),
                ("caaz", 3), ("baba", 3), ("abbb", 3),
                ("zaaz", 6), ("baba", 6), ("abbb", 6),
                ("baaa", 9), ("baba", 9), ("abbb", 9)]
        amplicons = bioa.Amplicons.build_uniform_amplicons(data, 4, 1, 13)
        eq_(4, len(amplicons), "amplicons aren't same length!")
        for amplicon in amplicons:
            for read in amplicon:
                eq_(len(read), 4, "read length is not 4!")

    def test_estimate_amplicons(self):
        # more cases with reads being cleaned out
        data = [("abbb", 0), ("aabb", 0), ("bbba", 0),
                ("caaz", 3), ("baba", 3), ("abbb", 3),
                ("zaaz", 6), ("baba", 6), ("abbb", 6),
                ("baaa", 9), ("baba", 9), ("abbb", 9)]
        amplicons = bioa.Amplicons.estimate_amplicons(data, 0, 13, 2, 100)
        pass

    def test_str(self):
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        # should built just fine
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        ok_(str(amplicons) is not None, "invalid string returned!")

    def test_len(self):
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        eq_(2, len(amplicons), "amplicons aren't same length!")

        # more cases with reads being cleaned out
        data = [("abbb", 0), ("aabb", 0), ("bbba", 0),
                ("caaz", 3), ("baba", 3), ("abbb", 3),
                ("zaaz", 6), ("baba", 6), ("abbb", 6),
                ("baaa", 9), ("baba", 9), ("abbb", 9)]
        se_pos = [(0, 4), (3, 7), (6, 10), (9, 13)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 13)
        eq_(4, len(amplicons), "amplicons aren't same length!")
