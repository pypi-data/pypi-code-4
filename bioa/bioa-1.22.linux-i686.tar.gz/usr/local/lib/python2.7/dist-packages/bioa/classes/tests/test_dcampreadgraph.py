#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nose.tools import *
import bioa
import math
import warnings

class TestDecliquedAmpliconReadGraph(object):

    def test_DecliquedAmpliconReadGraph(self):
        """
        """
        # test uniform equivalent case
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(7, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        # test non-uniform length, but equivalent overlap case
        data = [("abbb", 0), ("aabb", 0),
                ("bbaa", 2), ("bbba", 2)]
        se_pos = [(0, 4), (2, 6)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(7, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        # test non-uniform length, non-equivalent overlap
        data = [("abbb", 0), ("aabz", 0),
                ("bbaa", 2), ("bbba", 2)]
        se_pos = [(0, 4), (2, 6)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(6, len(graph), "number of nodes do not match")
        eq_(6, graph.size(), "number of edges do not match")

        # test non-uniform length, non-equivalent overlap
        data = [("abbb", 0), ("aabz", 0),
                ("bbaa", 2), ("bbba", 2)]
        se_pos = [(0, 4), (2, 6)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 6)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 1)
        eq_(7, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3),
                ("abab", 6), ("abbb", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(10, len(graph), "number of nodes do not match")
        eq_(12, graph.size(), "number of edges do not match")

        data = [("abbb", 0), ("aabb", 0), ("bbbb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(8, len(graph), "number of nodes do not match")
        eq_(10, graph.size(), "number of edges do not match")

        data = [("abbb", 0), ("aabb", 0), ("bbba", 0),
                ("baaa", 3), ("baba", 3), ("abbb", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        eq_(10, len(graph), "number of nodes do not match")
        eq_(12, graph.size(), "number of edges do not match")


    def test_read_frequency_correlation(self):
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        ograph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        # this test wont produce a correlation coefficient
        # because the variance is 0, hence, std-dev is 0
        corr, _ = graph.read_frequency_correlation(ograph)
        ok_(math.isnan(corr), "correlation not equivalent!")
