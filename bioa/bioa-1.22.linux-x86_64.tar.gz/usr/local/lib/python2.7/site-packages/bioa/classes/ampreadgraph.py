# -*- coding: utf-8 -*-
""" Base Amplicon ReadGraph class that allows typing errors. All more specific
    amplicon classes will inherit from this class.
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import bioa
import networkx as netx

from multiprocessing import Pool
from bioa.classes.readgraph import ReadGraph


class AmpliconReadGraph(ReadGraph):
    """
        Base Typing error-prone Amplicon ReadGraph class.
    """

    _OVERLAP = "overlap"

    def __init__(self, amplicons, err_tolerance, nthreads=1):
        """
        """
        ReadGraph.__init__(self)
        self.error_tolerance = err_tolerance
        self.set_amplicons(amplicons)
        self._build_base_amp_graph(amplicons, nthreads)

    @property
    def error_tolerance(self):
        return self._error_tolerance

    @error_tolerance.setter
    def error_tolerance(self, val):
        if val < 0:
            raise ValueError("number must be greater than  0!")
        self._error_tolerance = val

    def set_amplicons(self, amplicons):
        self.amplicons = amplicons

    def get_amplicons(self):
        return self.amplicons

    def get_start_end_positions(self):
        return self.amplicons.get_start_end_positions()

    def get_start_end_position_by_amplicon(self, amp_index):
        return self.amplicons.get_start_end_position(amp_index)

    def build_amplicons_from_graph(self, out_file, scale_factor):
        """
        """

        for node in self:
            read = self.get_node_read(node)
            freq = self.get_node_freq(node)
            pos = self.get_node_position(node)
            if read != "":
                for i in range(int(scale_factor * freq)):
                    out_file.write("{0}, {1}\n".format(read, pos))

        return

    def _build_base_amp_graph(self, amplicons, nthreads):
        """
        """
        if nthreads < 1:
            nthreads = 1

        def _clean_nodes(node, stop_node, degree_func, children_func):
            """ This does a DFS to recursively remove nodes that arent
                strongly connected.
            """
            if node == stop_node:
                return
            for child in children_func(node):
                _clean_nodes(child, stop_node, degree_func, children_func)

            # keep source and sink nodes, no matter what
            if degree_func(node) == 0 and \
                    (node != self.source and node != self.sink):
                self.remove_node(node)

            return

        # construct the frequency matrix and the empty graph
        freq_matrix = bioa.FrequencyMatrix.construct_normalized_freq_matrix(amplicons, True, nthreads)
        first = freq_matrix[0]
        last = freq_matrix[-1]
        height = len(first)

        def _id(i, j):
            return str(j * height + i)

        err_tol = self.error_tolerance
        source = self.source
        sink = self.sink

        self.add_node(source, "", 1.0, 0)
        self.add_node(sink, "", 1.0, 0)

        # add the source and sink edges to the graph
        rstart, end = self.get_start_end_position_by_amplicon(0)
        for rdx, pair in enumerate(first):
            rd, freq = pair
            rnode = _id(rdx, 0)
            self.add_node(rnode, rd, freq, rstart)
            if freq != 0:
                self.add_edge(source, rnode, freq)

        lstart, end = self.get_start_end_position_by_amplicon(len(amplicons) - 1)
        for rdx, pair in enumerate(last):
            rd, freq = pair
            lnode = _id(rdx, len(freq_matrix) - 1)
            self.add_node(lnode, rd, freq, lstart)
            if freq != 0:
                self.add_edge(lnode, sink, freq)

        # iterate over all amplicons except the last
        pool = Pool(nthreads)
        pool_obj = ReadGraphPoolObj(self)
        args = ((freq_matrix, column, cdx, err_tol)
                    for cdx, column in enumerate(freq_matrix[:-1]))
        edges, nodes = zip(*pool.map(pool_obj, args))
        #edges, nodes = zip(*map(pool_obj, args))

        for node_set in nodes:
            for node in node_set:
                node_data = node_set[node]
                self.add_node(*node_data)

        for edge_set in edges:
            self.add_edges_from(edge_set)

        # we may have to clean data (disjoint chains)
        self.graph.remove_nodes_from(netx.isolates(self.graph))
        _clean_nodes(self.source, self.sink, self.graph.out_degree, self.graph.successors)
        _clean_nodes(self.sink, self.source, self.graph.in_degree, self.graph.predecessors)

        return

    def _build_edges(self, freq_matrix, column, cdx, err_tol):
        """
        """
        height = len(column)
        def _id(i, j):
            return str(j * height + i)

        edges = []
        nodes = dict()
        # grab the neighboring amplicon
        ncolumn = freq_matrix[cdx + 1]
        start, end = self.get_start_end_position_by_amplicon(cdx)
        nstart, nend = self.get_start_end_position_by_amplicon(cdx + 1)
        overlap = end - nstart

        # add each unique read in this column to the graph and
        # check for consistency in the neighboring amplicon
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # this could be sped up to run faster if we ran bucket sort
        # on the neighboring column based on the overlap
        # and then only matched with the necessary bucket
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for rdx, pair in enumerate(column):
            rd, freq = pair
            # do not add empty reads to the graph
            if freq == 0:
                continue

            # we will keep the actual read and read frequency as metadata
            # in the graph
            lnode = _id(rdx, cdx)
            for nrdx, npair in enumerate(ncolumn):
                nread, nfreq = npair
                if nfreq == 0:
                    continue

                rnode = _id(nrdx, cdx + 1)
                if rnode not in nodes:
                    nodes[rnode] = (rnode, nread, nfreq, nstart)

                # if the two reads are consistent with one another
                # given the overlap amount, add an edge to the graph
                if bioa.are_consistent(rd, nread, overlap, err_tol):
                    edges.append((lnode, rnode, {self.COUNT: 1.0}))

        return edges, nodes

class ReadGraphPoolObj(object):
    """
    """
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, args):
        return self.cls._build_edges(*args)
