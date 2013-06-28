"""
=======================
Graph Utility Functions
=======================
"""

__all__ = ["max_bandwidth",
           "graph_rank"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import sys
import networkx as nx
import bioa as ba


def max_bandwidth(graph, source="source", freq_name="count", epsilon=1e-3):
    """ Given a graph G = (V,E) with capacity over vertices and a source,
        find the set of paths which maximize the bandwidth (minimize the
        bottleneck) from the source.

        Parameters
        ----------
        graph : NetworkX Graph
            Graph to find the maximum bandwidth path of.

        source : str (optional, default="source")
            Name of the source vertex to begin the search from.

        freq_name : str (optional, default="count")
            Name of the frequency or count property to use.

        epsilon : float (optional, default=1e-3)
            Threshold for edge values to consider.

        Returns
        -------
        bandwidth_and_paths : (dict, dict) tuple
            Dictionary of the bandwidth from the source to a node along with
            the dictionary of the maximum bandwidth path from a source to a
            node.
    """

    bwidths = {}  # dictionary of final bandwidths
    paths = {source: [source]}  # dictionary of paths
    seen = {source: sys.maxint}
    fringe = ba.PQueue([(sys.maxint, source)], behave="max")

    while len(fringe) > 0:
        v, b = fringe.get_max()
        if v in bwidths:
            continue   # already searched this node.
        bwidths[v] = b

        edata = iter(graph[v].items())

        for w, edgedata in edata:
            vw_band = min([bwidths[v], edgedata[freq_name]])

            if vw_band > seen.get(w, epsilon):
                seen[w] = vw_band
                fringe.add_node(vw_band, w)
                paths[w] = paths[v] + [w]

    return (bwidths, paths)


def graph_rank(graph):
    """ Rank of an undirected graph is defined as n - c where n is the
        number of vertices in the graph and c is the number of connected
        components of the graph. This is the same rank as the representative
        incidence matrix.

        Parameters
        ----------
        graph : NetworkX Graph
            Undirected graph.

        Returns
        -------
        rank : int
            Rank of the graph.
    """
    if graph is None:
        raise ValueError("Valid graph must be used!")
    if graph.is_directed():
        raise ValueError("Rank of a directed graph not defined")

    ncount = len(graph)
    nconcomps = nx.number_connected_components(graph)
    return ncount - nconcomps
