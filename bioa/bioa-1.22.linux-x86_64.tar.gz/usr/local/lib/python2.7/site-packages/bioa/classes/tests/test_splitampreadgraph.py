#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nose.tools import *
import bioa

class TestSplitAmpliconReadGraph(object):

    def test_SplitAmpliconReadGraph(self):
        """ All unique reads in the read matrix will result in two vertices,
            v and v' in the graph. All frequency values for a read will be
            the frequency value of the edge, v -> v'. All left consistent reads
            will be an edge from v' -> u. All right consistent reads will be an
            edge from u' -> v.
        """

        data = [("abab", 0), ("baba", 0), ("abab", 0),
                ("agcg", 3), ("btgt", 3), ("btgt", 3),
                ("gtat", 6), ("tata", 6), ("ttta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)

        # there should be 16 nodes and 17 edges
        eq_(16, len(graph), "number of nodes do not match")
        eq_(17, graph.size(), "number of edges do not match")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)

        # there should be 16 nodes and 17 edges
        eq_(16, len(graph), "number of nodes do not match")
        eq_(17, graph.size(), "number of edges do not match")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)

        # there should be 16 nodes and 17 edges
        eq_(16, len(graph), "number of nodes do not match")
        eq_(17, graph.size(), "number of edges do not match")
