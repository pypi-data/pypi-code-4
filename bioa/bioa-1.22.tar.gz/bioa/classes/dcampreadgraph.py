# -*- coding: utf-8 -*-
""" Decliqued Amplicon ReadGraph class.
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import uuid
import bioa
import scipy.stats as stats
import networkx as nx
import networkx.algorithms.bipartite as bipartite

from bioa.classes.ampreadgraph import AmpliconReadGraph

class DecliquedAmpliconReadGraph(AmpliconReadGraph):
    """ Decliqued Amplicon ReadGraph class.
    """

    UNBALANCED = 0
    BALANCED = 1

    def __init__(self, amplicons, err_threshold, balance=UNBALANCED, nthreads=1):
        """
        """
        AmpliconReadGraph.__init__(self, amplicons, err_threshold, nthreads=nthreads)
        self._build_decliqued_graph(balance)

    def _get_frequency_pairs(self, graph):
        """
        """
        read_nodes = set(self.get_read_nodes())
        mread_nodes = set(graph.get_read_nodes())
        mread_map = {graph.get_node_read(node): node for node in mread_nodes}
        mread_set = set(mread_map.keys())

        freqs = []
        gfreqs = []

        # if either have any reads not in the other graph, just mark as 0
        # additionally, this assumes there are no repeats of reads
        for node in read_nodes:
            read = self.get_node_read(node)
            freqs.append(self.get_node_freq(node))

            if read not in mread_set:
                gfreqs.append(0.0)
            else:
                mread_set.remove(read)
                gfreqs.append(graph.get_node_freq(mread_map[read]))

        # if any leftover in mread_set, add them as well
        for read in mread_set:
            freqs.append(0.0)
            gfreqs.append(graph.get_node_freq(mread_map[read]))

        return (freqs, gfreqs)

    def get_read_nodes(self):
        """ Get the reads in the decliqued read-graph

            Parameters
            ----------
            None

            Returns
            -------
            reads : set
                Set of reads in the read graph.
        """
        reads, _ = self.get_read_and_fork_nodes()
        return reads

    def get_fork_nodes(self):
        """ Get the forks in the decliqued read-graph

            Parameters
            ----------
            None

            Returns
            -------
            forks : set
                Set of forks in the read graph.
        """
        _, forks = self.get_read_and_fork_nodes()
        return forks

    def get_read_and_fork_nodes(self):
        """ Get the reads and forks in the decliqued read-graph

            Parameters
            ----------
            None

            Returns
            -------
            reads_and_forks : (set, set)
                Tuple of the read-set and the fork-set.
        """
        src = self.source
        forks, reads = bipartite.sets(self.graph)
        if src in reads:
            tmp = forks
            forks = reads
            reads = tmp

        return reads, forks

    def split_fork(self, fork, left, right, minmax):
        """ Split a fork node into two seperate nodes:
            One for each read (left and right)

            Parameters
            ----------
            fork : Vertex
                Fork vertex in the graph.

            left : Vertex
                Read that is an immediate predecessor of the fork.

            right : Vertex
                Read that is an immediate successor of the fork.

            minmax : float/int
                Frequency/count to assign over new edge.

            Returns
            -------
            new_fork : Vertex
                New fork that split from parameter.
        """
        if fork not in self:
            raise ValueError("Fork {0} is not in the graph!".format(fork))
        elif left not in self:
            raise ValueError("Node {0} is not in the graph!".format(left))
        elif right not in self:
            raise ValueError("Node {0} is not in the graph!".format(right))

        nfork = fork + str(uuid.uuid4())
        assert nfork not in self, "Duplicate split node!"

        nfread = self.get_node_read(fork)
        nfpos = self.get_node_position(fork)
        self.add_node(nfork, nfread, minmax, nfpos)
        self.add_edge(left, nfork, minmax)
        self.add_edge(nfork, right, minmax)
        return nfork

    def split_edge(self, fork, left, right, minmax):
        """ Split a fork as well as the left and right nodes into new nodes
            with the given minmax. The original nodes will have their counts
            reduced

            Parameters
            ----------
            fork : Vertex
                Fork vertex in the graph.

            left : Vertex
                Read that is an immediate predecessor of the fork.

            right : Vertex
                Read that is an immediate successor of the fork.

            minmax : float/int
                Frequency/count to assign over new edge.

            Returns
            -------
            double_edge : Tuple
                (NewLeft, NewFork, NewRight) tuple that was just added.
        """
        if fork not in self:
            raise ValueError("Fork {0} is not in the graph!".format(fork))
        elif left not in self:
            raise ValueError("Node {0} is not in the graph!".format(left))
        elif right not in self:
            raise ValueError("Node {0} is not in the graph!".format(right))

        # create a unique id to append for new nodes
        sid = str(uuid.uuid4())
        nfork = fork + sid
        nleft = left + sid
        nright = right + sid

        assert nfork not in self, "Duplicate split node!"
        assert nleft not in self, "Duplicate split node!"
        assert nright not in self, "Duplicate split node!"

        nfread = self.get_node_read(fork)
        nlread = self.get_node_read(left)
        nrread = self.get_node_read(right)

        nfpos = self.get_node_position(fork)
        nlpos = self.get_node_position(left)
        nrpos = self.get_node_position(right)

        # add new nodes to self
        self.add_node(nfork, nfread, minmax, nfpos)
        self.add_node(nleft, nlread, minmax, nlpos)
        self.add_node(nright, nrread, minmax, nrpos)

        # add new edges
        for pred in self.predecessors(left):
            self.add_edge(pred, nleft, minmax)

        for succ in self.successors(right):
            self.add_edge(nright, succ, minmax)

        self.add_edge(nleft, nfork, minmax)
        self.add_edge(nfork, nright, minmax)

        return (nleft, nfork, nright)

    def read_frequency_correlation(self, graph):
        """ Computes the correlation between the frequencies of the reads
            in this graph versus the frequences of the reads in the other
            graph.

            Parameters
            ----------
            self : DecliquedAmpliconReadGraph
                Original amplicon read graph

            graph : DecliquedAmpliconReadGraph
                Adjusted read frequency amplicon read self with fork
                vertices added.

            Returns
            -------
            correlation_and_p_value : (float, float)
                Pearson's correlation coefficient between the two frequency
                data sets and the corresponding p-value.
        """
        if not graph:
            raise ValueError("Non-empty Read-Graph expected!")

        freqs, gfreqs = self._get_frequency_pairs(graph)
        return stats.pearsonr(freqs, gfreqs)

    def read_frequency_squared_euclidean_distance(self, graph):
        """ Computes the squared euclidean distance between the frequencies of
            the reads in this graph versus the frequences of the reads in the
            other graph.

            Parameters
            ----------
            self : DecliquedAmpliconReadGraph
                Original amplicon read graph

            graph : DecliquedAmpliconReadGraph
                Adjusted read frequency amplicon read self with fork
                vertices added.

            Returns
            -------
            distance_squared : float
                Sum of all the squared distances.
        """
        if not graph:
            raise ValueError("Non-empty Read-Graph expected!")

        freqs, gfreqs = self._get_frequency_pairs(graph)
        total = 0.0
        for freq, gfreq in zip(freqs, gfreqs):
            total += (freq - gfreq)**2.0

        return total

    def _build_decliqued_graph(self, balance=BALANCED):
        """
            We wish to take all bipartite cliques (bicliques) and
            reprsent them by adding a "clique" node. This will make
            bicliques representable by m + n edges instead of
            m * n, if m = |V|_1, n = |V|_2.

            Example:

            o-----o               o       o
             \   /                  \   /
               x       becomes        o"
             /  \                   /   \
            o----o                o       o
        """
        cid = 0
        clique = "clique0"

        src = self.source
        snk = self.sink
        done = set([src, snk])

        # its easier to just build a new graph for this than to delete edges
        dcgraph = bioa.ReadGraph()
        dcgraph.add_nodes_from(self.graph.nodes(data=True))

        for node in self.successors(src):
            freq = self.get_node_freq(node)
            dcgraph.add_edge(src, node, count=freq)

        for node in self.predecessors(snk):
            freq = self.get_node_freq(node)
            dcgraph.add_edge(node, snk, count=freq)

        for node, _ in nx.bfs_edges(self.graph, src):
            if node in done:
                continue

            succs = self.successors(node)
            if succs and succs[0] != snk:
                nbr = succs[0]
                preds = self.predecessors(nbr)

                # we need to scale the graph
                psum = sum(dcgraph.get_node_freq(pred) for pred in preds)
                ssum = sum(dcgraph.get_node_freq(succ) for succ in succs)
                ratio = psum / float(ssum)
                dcgraph.add_node(clique, "", psum, 0)
                for succ in succs:
                    freq = self.get_node_freq(succ)
                    nfreq = freq * ratio if balance else freq
                    dcgraph.set_node_freq(succ, nfreq)
                    dcgraph.add_edge(clique, succ, nfreq)

                for pred in preds:
                    freq = self.get_node_freq(pred)
                    dcgraph.add_edge(pred, clique, freq)

                done = done | set(preds)
                cid += 1
                clique = "clique" + str(cid)

        self.graph.clear()
        self.add_nodes_from(dcgraph.graph.nodes(data=True))
        self.add_edges_from(dcgraph.graph.edges(data=True))
        self.set_node_freq(src, 1.0)
        self.set_node_freq(snk, 1.0)
        return
