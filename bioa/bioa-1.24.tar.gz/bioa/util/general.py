# -*- coding: utf-8 -*-
"""
=========================
General utility functions
=========================
"""

__all__ = ["are_consistent",
           "reconstruct_sequence",
           "reconstruct_uniform_sequence",
           "convert_networkx_to_read_graph"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import bioa
import networkx as nx


def are_consistent(read_one, read_two, overlap, error_tolerance=0):
    """ Checks if the two reads are consistent within the threshold.

        Parameters
        ----------
        read_one : str
            First read whose tail must match.

        read_two : str
            The other read whose head must much.

        overlap : int
            The amount the reads overlap by.

        error_tolerance : int (optional, default=0)
            The number of allowable errors.

        Returns
        -------
        are_consitent : bool
            True if consistent, False otherwise.
    """
    str1 = read_one[len(read_one) - overlap:]
    str2 = read_two[:overlap]
    if len(str1) != len(str2):
        raise ValueError("Strings must be equal in length!")

    differences = bioa.hamming_distance(str1, str2)
    return differences <= error_tolerance


def reconstruct_uniform_sequence(reads, overlap):
    """
    """
    if not reads:
        raise ValueError("Reads must be defined to reconstruct a sequence!")
    if overlap < 1:
        raise ValueError("Valid overlap length must be defined to build " + \
                        "amplicons!")

    reads = [read for read in reads if bool(read)]
    freads = [reads[0]] + [read[overlap:] for read in reads[1:]]
    return "".join(freads)


def reconstruct_sequence(reads, start_end_positions):
    """
    """
    if not reads:
        raise ValueError("Reads must be defined to reconstruct a sequence!")
    if not start_end_positions:
        raise ValueError(
                "Valid overlap lengths must be defined to build amplicons!")
    reads = [read for read in reads if bool(read)]
    freads = []
    lend = start_end_positions[0][0]
    for idx, read in enumerate(reads):
        start, end = start_end_positions[idx]
        freads.append(read[lend - start:])
        lend = end

    return "".join(freads)


def convert_networkx_to_read_graph(graph, source="source", sink="sink"):
    """
    """
    if graph is None or not isinstance(graph, nx.Graph):
        raise ValueError("Expected networkx graph!")

    rg = bioa.ReadGraph(source, sink)
    rg.graph.update(graph.graph)
    rg.add_nodes_from(graph.nodes_iter(data=True))
    rg.add_edges_from(graph.edges_iter(data=True))
    return rg
