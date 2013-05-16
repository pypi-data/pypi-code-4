#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
import bioa


class TestReadGraph(object):

    def test_read_graph_init(self):
        rgraph = bioa.ReadGraph()
        ok_(rgraph is not None, "empty read graph!")

    def test_len_read_graph(self):
        rgraph = bioa.ReadGraph()
        eq_(len(rgraph), 2, "read graph len not equal to 2")

        rgraph.add_node(0, 'test', 0.0, 0)
        eq_(len(rgraph), 3, "read graph len not equal to 3")

    def test_size_read_graph(self):
        rgraph = bioa.ReadGraph()
        eq_(rgraph.size(), 0, "read graph size not equal to 0")

        rgraph.add_node(0, 'test', 0.0, 0)
        rgraph.add_node(1, 'test', 0.0, 0)
        rgraph.add_edge(0, 1, 0)
        eq_(rgraph.size(), 1, "read graph size not equal to 1")

    def test_iter_read_graph(self):
        rgraph = bioa.ReadGraph()
        eq_(rgraph.size(), 0, "read graph size not equal to 0")

        rgraph.add_node(0, 'test', 0.0, 0)
        rgraph.add_node(1, 'test', 0.0, 0)

        itbl = iter(rgraph)
        ok_(itbl is not None, "read graph is not iterable")
