""" Base ReadGraph class. All more specific classes will inherit from this
class. This is a base data structure for reads of sequences.
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import networkx as nx


class ReadGraph(object):
    """ Base ReadGraph class.
    """
    SOURCE = "source"
    SINK = "sink"
    COUNT = "count"
    READ = "read"
    POS = "pos"

    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph.add_node(self.__class__.SOURCE, demand=-1.0)
        self.graph.add_node(self.__class__.SINK, demand=1.0)

    def __iter__(self):
        return iter(self.graph)

    def __len__(self):
        return len(self.graph)

    def size(self):
        return self.graph.size()

    @property
    def source(self):
        return self.__class__.SOURCE

    @property
    def sink(self):
        return self.__class__.SINK

    def successors(self, node):
        return self.graph.successors(node)

    def successors_iter(self, node):
        return self.graph.successors_iter(node)

    def predecessors_iter(self, node):
        return self.graph.predecessors_iter(node)

    def predecessors(self, node):
        return self.graph.predecessors(node)

    def add_node(self, node, read, freq, pos):
        self.graph.add_node(node, read=read, count=freq, pos=pos)

    def remove_node(self, node):
        self.graph.remove_node(node)

    def add_nodes_from(self, nodes):
        self.graph.add_nodes_from(nodes)

    def remove_nodes_from(self, nodes):
        self.graph.remove_nodes_from(nodes)

    def add_edge(self, lnode, rnode, count, **kwargs):
        self.graph.add_edge(lnode, rnode, kwargs, count=count)

    def add_edges_from(self, edge_list, **kwargs):
        for e in edge_list:
            ne = len(e)
            if ne == 3:
                # count is included
                u, v, dd = e
            elif ne == 2:
                u, v, = e
                dd = {}
            else:
                raise ValueError("Expected edge data type! (u, v)")
            datadict = {}
            datadict.update(kwargs)
            datadict.update(dd)
            self.add_edge(u, v, **datadict)

    def remove_edge(self, u, v):
        self.graph.remove_edge(u, v)

    def remove_edges_from(self, edge_list):
        self.graph.remove_edges_from(edge_list)

    def get_node_freq(self, node):
        """
            get_node_freq: returns the frequency of the
                read that the node represents

            node: the node in the graph

        """
        return self.graph.node[node][self.__class__.COUNT]

    def set_node_freq(self, node, freq):
        self.graph.node[node][self.__class__.COUNT] = freq
        return

    def get_edge_freq(self, node1, node2):
        return self.graph[node1][node2][self.__class__.COUNT]

    def set_edge_freq(self, node1, node2, freq):
        self.graph[node1][node2][self.__class__.COUNT] = freq

    def get_node_read(self, node):
        return self.graph.node[node][self.__class__.READ]

    def set_node_read(self, node, read):
        self.graph.node[node][self.__class__.READ] = read
        return

    def get_node_read_len(self, node):
        return len(self.graph.node[node][self.__class__.READ])

    def get_node_position(self, node):
        return self.graph.node[node][self.__class__.POS]

    def set_node_position(self, node, pos):
        self.graph.node[node][self.__class__.POS] = pos
        return

    def is_fork(self, node):
        return self.graph.out_degree(node) > 1

    def get_forks(self):
        source = self.source
        return  [node for node in self if self.is_fork(node) and node != source]
