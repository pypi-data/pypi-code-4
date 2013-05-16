#!/usr/bin/env python
from nose.tools import *
import bioa
import networkx as nx

class TestGraphUtil:

    def test_max_bandwidth(self):
        '''
        '''
        graph = nx.Graph()
        graph.add_edge(0, 1, count=5)
        graph.add_edge(1, 2, count=3)
        graph.add_edge(2, 3, count=5)

        bws, pts = bioa.max_bandwidth(graph, source=0)
        tpath = pts[3]
        eq_(bws[3], 3, 'maximum bandwidth does not match')
        eq_(tpath[0], 0, 'maximum bandwidth does not match')
        eq_(tpath[1], 1, 'maximum bandwidth does not match')
        eq_(tpath[2], 2, 'maximum bandwidth does not match')
        eq_(tpath[3], 3, 'maximum bandwidth does not match')

        graph = nx.Graph()
        graph.add_edge(0, 1, count=5)
        graph.add_edge(1, 2, count=3)
        graph.add_edge(2, 3, count=5)
        graph.add_edge(0, 4, count=5)
        graph.add_edge(4, 5, count=5)
        graph.add_edge(5, 3, count=5)

        bws, pts = bioa.max_bandwidth(graph, source=0)
        tpath = pts[3]
        eq_(bws[3], 5, 'maximum bandwidth does not match')
        eq_(tpath[0], 0, 'maximum bandwidth does not match')
        eq_(tpath[1], 4, 'maximum bandwidth does not match')
        eq_(tpath[2], 5, 'maximum bandwidth does not match')
        eq_(tpath[3], 3, 'maximum bandwidth does not match')

        # reduce the edges on the max bandwidth path
        for idx, v in enumerate(tpath[:-1]):
            next = tpath[idx+1]
            graph[v][next]['count'] -= 5

        # we should not get the same results back, we should get 
        # the same as the first round of tests.
        bws, pts = bioa.max_bandwidth(graph, source=0)
        tpath = pts[3]
        eq_(bws[3], 3, 'maximum bandwidth does not match')
        eq_(tpath[0], 0, 'maximum bandwidth does not match')
        eq_(tpath[1], 1, 'maximum bandwidth does not match')
        eq_(tpath[2], 2, 'maximum bandwidth does not match')
        eq_(tpath[3], 3, 'maximum bandwidth does not match')

    def test_graph_rank(self):
        pass
