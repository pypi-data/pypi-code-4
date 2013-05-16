"""
    Split-Read Amplicon ReadGraph class.
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

from bioa.classes.ampreadgraph import AmpliconReadGraph


class SplitAmpliconReadGraph(AmpliconReadGraph):
    """
        Split-Read Amplicon ReadGraph class.
    """

    def __init__(self, amplicons, err_tol):
        AmpliconReadGraph.__init__(self, amplicons, err_tol)
        self._build_split_amp_graph()

    @classmethod
    def convert_decliqued_readgraph(cls, dcgraph):
        graph = cls(dcgraph.get_amplicons(), dcgraph.error_tolerance)
        for node in dcgraph:
            if node in [dcgraph.source, dcgraph.sink]:
                continue
            nfreq = dcgraph.get_node_freq(node)
            graph.set_node_freq(node, nfreq)
            graph.set_node_freq(node + "'", nfreq)

        return graph

    def get_read_nodes(self):
        return [node for node in self.graph.nodes() if node not in [self.sink, self.sink]]

    def _build_split_amp_graph(self):
        """
            Build a graph given the amplicons where vertices
            are the unique reads in the matrix and edges are
            the consistent reads.

        """

        # we need to split reads so that frequencies can be over edges
        source = self.source
        sink = self.sink

        for rd, data in self.graph.nodes(data=True):
            if rd in [source, sink]:
                continue

            readprime = rd + "'"
            fdata = data[self.__class__.COUNT]
            pdata = data[self.__class__.POS]

            self.add_node(readprime, "", fdata, pdata)

            # get the out edges and remove them
            oedges = self.graph.out_edges(rd)
            self.remove_edges_from(oedges)

            # re-add them from readprime
            oedges = [(readprime, nbr) for _, nbr in oedges]
            self.add_edges_from(oedges, count=1.0, weight=1.0)

            # add an edge between read and readprime with the count
            self.add_edge(rd, readprime, fdata)
        return
