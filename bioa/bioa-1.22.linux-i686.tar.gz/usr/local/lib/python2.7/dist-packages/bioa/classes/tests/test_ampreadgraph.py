#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nose.tools import *
import bioa

class TestAmpliconReadGraph(object):

    def test_AmpliconReadGraph(self):
        """
        """
        # test uniform equivalent case
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.AmpliconReadGraph(amplicons, 0)
        eq_(6, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        # test non-uniform length, but equivalent overlap case
        data = [("abbb", 0), ("aabb", 0),
                ("bbaa", 2), ("bbba", 2)]
        se_pos = [(0, 4), (2, 6)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.AmpliconReadGraph(amplicons, 0)
        eq_(6, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        # 'aabz' should be cleaned out
        data = [("abbb", 0), ("aabz", 0),
                ("bbaa", 2), ("bbba", 2)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.AmpliconReadGraph(amplicons, 0)
        eq_(5, len(graph), "number of nodes do not match")
        eq_(5, graph.size(), "number of edges do not match")

        # test non-uniform length, non-equivalent overlap
        data = [("abbb", 0), ("aabz", 0),
                ("bbaa", 2), ("bbba", 2)]
        se_pos = [(0, 4), (2, 6)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.AmpliconReadGraph(amplicons, 2)
        eq_(6, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        # more cases with reads being cleaned out
        data = [("abbb", 0), ("aabb", 0), ("bbba", 0),
                ("caaz", 3), ("baba", 3), ("abbb", 3),
                ("zaaz", 6), ("baba", 6), ("abbb", 6),
                ("baaa", 9), ("baba", 9), ("abbb", 9)]
        se_pos = [(0, 4), (3, 7), (6, 10), (9, 13)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 13)
        graph = bioa.AmpliconReadGraph(amplicons, 0)
        eq_(14, len(graph), "number of nodes do not match")
        eq_(15, graph.size(), "number of edges do not match")
