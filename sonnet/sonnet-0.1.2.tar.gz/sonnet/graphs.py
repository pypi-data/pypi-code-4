# -*- coding: utf-8 -*-
import functools
import json
import random
import networkx as nx
from networkx.readwrite import json_graph
from betweenness_centrality_helpers import (
    _single_source_shortest_path_basic, _single_source_dijkstra_path_basic,
    _accumulate_endpoints, _accumulate_basic, _rescale
)


class SonnetException(Exception):
    pass


class Sonnet(object):

    def __init__(self, graph, name=None, max_node_size=6, min_node_size=1,
                 rank_by='degree_centrality', color_by='community'):
        self.graph = graph
        self.name = name
        self.max_node_size = max_node_size
        self.min_node_size = min_node_size
        self.rank_by = rank_by
        self.color_by = color_by

    def __getitem__(self, node):
        return self.graph.node[node]

    def __len__(self):
        return len(self.graph.nodes())

    def __iter__(self):
        return iter(self.graph.node)

    def is_multigraph(self):
        return self.graph.is_multigraph()

    def nodes(self):
        node_list = [node for node in self.sonnet_nodes_iter()]
        return node_list

    def add_attr(self, attr, value):
        for node in self.nodes_iter():
            self[node][attr] = value

    def get_attr(self, attr):
        try:
            attr_dict = {
                node: a for (node, a) in self.attr_iter(attr)
            }
        except KeyError:
            raise SonnetException('Attr does not exist')
        return attr_dict

    def degree(self):
        for node, degree in self.graph.degree_iter():
            self[node]['degree'] = degree

    def get_degree(self):
        try:
            degree_dict = {
                node: d for (node, d) in self.sonnet_degree_iter()
            }
        except KeyError:
            print('Calculating degree.')
            self.degree()
            degree_dict = {
                node: d for (node, d) in self.sonnet_degree_iter()
            }
        return degree_dict

    def degree_centrality(self):
        normal = 1.0 / (len(self) - 1.0)
        for node, degree in self.graph.degree_iter():
            self[node]['degree_centrality'] = degree * normal

    def get_degree_centrality(self):
        try:
            degree_cent_dict = {
                node: dc for (node, dc) in self.degree_centrality_iter()
            }
        except KeyError:
            print('Calculating degree centrality')
            self.degree_centrality()
            degree_cent_dict = {
                node: dc for (node, dc) in self.degree_centrality_iter()
            }
        return degree_cent_dict

    def in_degree_centrality(self):
        if not self.graph.is_directed():
            msg = "in_degree_centrality() not defined for undirected graphs."
            raise nx.NetworkXError(msg)
        normal = 1.0 / (len(self) - 1.0)
        for node, degree in self.graph.in_degree_iter():
            self[node]['in_degree_centrality'] = degree * normal

    def get_in_degree_centrality(self):
        try:
            in_degree_cent_dict = {
                node: idc for (node, idc) in self.in_degree_centrality_iter()
            }
        except KeyError:
            print('Calculating in-degree centrality')
            self.in_degree_centrality()
            in_degree_cent_dict = {
                node: idc for (node, idc) in self.in_degree_centrality_iter()
            }
        return in_degree_cent_dict

    def out_degree_centrality(self):
        if not self.graph.is_directed():
            msg = "out_degree_centrality() not defined for undirected graphs."
            raise nx.NetworkXError(msg)
        normal = 1.0 / (len(self) - 1.0)
        for node, degree in self.graph.out_degree_iter():
            self[node]['out_degree_centrality'] = degree * normal

    def get_out_degree_centrality(self):
        try:
            out_degree_cent_dict = {
                node: odc for (node, odc) in self.out_degree_centrality_iter()
            }
        except KeyError:
            print('Calculating out-degree centrality')
            out_degree_cent_dict = {
                node: odc for (node, odc) in self.out_degree_centrality_iter()
            }
        return out_degree_cent_dict

    def closeness_centrality(self, distance=None, normalized=True):
        """
        Adapted from NetworkX closeness centrality measures.
        https://github.com/networkx/networkx/blob/master/
                networkx/algorithms/centrality/closeness.py
        """
        #    Copyright (C) 2004-2013 by
        #    Aric Hagberg <hagberg@lanl.gov>
        #    Dan Schult <dschult@colgate.edu>
        #    Pieter Swart <swart@lanl.gov>
        #    All rights reserved.
        #    BSD license.
        if distance is not None:
            # use Dijkstra's algorithm with specified attribute as edge weight
            path_length = functools.partial(
                nx.single_source_dijkstra_path_length, weight=distance
            )
        else:
            path_length = nx.single_source_shortest_path_length
        nodes = self.graph.nodes()
        for n in nodes:
            sp = path_length(self.graph, n)
            totsp = sum(sp.values())
            if totsp > 0.0 and len(self) > 1:
                self[n]['closeness_centrality'] = (len(sp) - 1.0) / totsp
                # normalize to number of nodes-1 in connected part
                if normalized:
                    s = (len(sp) - 1.0) / (len(self) - 1.0)
                    self[n]['closeness_centrality'] *= s
            else:
                self[n]['closeness_centrality'] = 0.0

    def betweenness_centrality(self, k=None, normalized=True, weight=None,
                               endpoints=False, seed=None):
        """
        Adapted from NetworkX betweenness centrality measures.
        https://github.com/networkx/networkx/blob/master/
                networkx/algorithms/centrality/betweenness.py
        """
        #    Copyright (C) 2004-2011 by
        #    Aric Hagberg <hagberg@lanl.gov>
        #    Dan Schult <dschult@colgate.edu>
        #    Pieter Swart <swart@lanl.gov>
        #    All rights reserved.
        #    BSD license.
        self.add_attr('betweenness_centrality', 0.0)
        if k is None:
            nodes = self.graph
        else:
            random.seed(seed)
            nodes = random.sample(self.graph.nodes(), k)
        for s in nodes:
            # single source shortest paths
            if weight is None:  # use BFS
                S, P, sigma = _single_source_shortest_path_basic(self.graph, s)
            else:  # use Dijkstra's algorithm
                S, P, sigma = _single_source_dijkstra_path_basic(
                    self.graph, s, weight=weight
                )
            # accumulation
            if endpoints:
                _accumulate_endpoints(self, S, P, sigma, s)
            else:
                _accumulate_basic(self, S, P, sigma, s)
        # rescaling
        _rescale(self, len(self), normalized=normalized,
                 directed=self.graph.is_directed(), k=k)

    def eigenvector_centrality(self, max_iter=100, tol=1.0e-6,
                               nstart=None, weight='weight'):
        """
        Adapted from NetworkX eigenvector centrality measures.
        https://github.com/networkx/networkx/blob/
            master/networkx/algorithms/centrality/eigenvector.py
        """
        #    Copyright (C) 2004-2011 by
        #    Aric Hagberg <hagberg@lanl.gov>
        #    Dan Schult <dschult@colgate.edu>
        #    Pieter Swart <swart@lanl.gov>
        #    All rights reserved.
        #    BSD license.
        from math import sqrt
        if self.is_multigraph() is True:
            raise nx.NetworkXException('Eigenvector centrality '
                                       'not defined for multigraphs.')

        if len(self) == 0:
            raise nx.NetworkXException("Empty graph.")

        if nstart is None:
            # choose starting vector with entries of 1/len(G)
            self.add_attr('eigenvector_centrality', 1.0/len(self))
            #x = dict([(n,1.0/len(G)) for n in G])
        else:
            self.add_attr('eigenvector_centrality', nstart)
            #x = nstart
        # normalize starting vector
        sx = 1.0/sum(self.get_eigenvector_centrality().values())
        for k in self.nodes_iter():
            self[k]['eigenvector_centrality'] *= sx
        nnodes = self.graph.number_of_nodes()
        # make up to max_iter iterations
        for i in range(max_iter):
            xlast = self.get_eigenvector_centrality()
            x = dict.fromkeys(xlast, 0)
            # do the multiplication y=Ax
            for n in x:
                for nbr in self.graph[n]:
                    self[n]['eigenvector_centrality'] += \
                        xlast[nbr]*self.graph[n][nbr].get(weight, 1)
            # normalize vector
            try:
                sx = 1.0/sqrt(
                    sum(v**2 for v in
                        self.get_eigenvector_centrality().values())
                )
            # this should never be zero?
            except ZeroDivisionError:
                sx = 1.0
            for n in x:
                self[n]['eigenvector_centrality'] *= sx
            # check convergence
            err = sum([
                abs(self[n]['eigenvector_centrality']-xlast[n]) for n in x
            ])
            if err < nnodes*tol:
                return None

        raise nx.NetworkXError("""eigenvector_centrality():
    power iteration failed to converge in %d iterations."%(i+1))""")

    def get_closeness_centrality(self):
        try:
            closeness_cent_dict = {
                node: cdc for (node, cdc) in self.closeness_centrality_iter()
            }
        except KeyError:
            print('Calculating closeness centrality.')
            self.closeness_centrality()
            closeness_cent_dict = {
                node: cdc for (node, cdc) in self.closeness_centrality_iter()
            }
        return closeness_cent_dict

    def get_betweenness_centrality(self):
        try:
            betweenness_cent_dict = {
                node: bc for (node, bc) in self.betweenness_centrality_iter()
            }
        except KeyError:
            print('Calculating betweenness centrality.')
            self.betweenness_centrality()
            betweenness_cent_dict = {
                node: bc for (node, bc) in self.betweenness_centrality_iter()
            }
        return betweenness_cent_dict

    def get_eigenvector_centrality(self):
        try:
            eigenvector_degree_cent_dict = {
                node: ec for (node, ec) in self.eigenvector_centrality_iter()
            }
        except KeyError:
            print('Calculating eigenvector centrality.')
            self.eigenvector_centrality()
            eigenvector_degree_cent_dict = {
                node: ec for (node, ec) in self.eigenvector_centrality_iter()
            }
        return eigenvector_degree_cent_dict

    def rank_nodes(self, rank_by=None, max_node_size=None, min_node_size=1):
        if not rank_by:
            if self.rank_by:
                rank_by = self.rank_by
            else:
                msg = ('Please set rank_by to determine size distribution')
                raise SonnetException(msg)
        if not max_node_size:
            if self.max_node_size:
                max_node_size = self.max_node_size
            else:
                raise SonnetException('Please enter max_node_size for nodes')
        if not min_node_size:
            if self.min_node_size:
                min_node_size = self.min_node_size
            else:
                raise SonnetException('Please enter max_node_size for nodes')
        data_dict = self.get_attr(rank_by)
        values = data_dict.values()
        max_value = max(values)
        min_value = min(values)
        value_range = float(max_value - min_value)
        for key, value in data_dict.items():
            value_difference = value - min_value
            if value_difference == 0:
                ranking = '{0}_ranking'.format(rank_by)
                self[key][ranking] = min_node_size
            else:
                value_fraction = value_difference / value_range
                size_fraction = (max_node_size -
                                 min_node_size) * value_fraction
                ranking = '{0}_ranking'.format(rank_by)
                self[key][ranking] = size_fraction + min_node_size

    def get_ranking(self, measure):
        rank_string = '{0}_ranking'.format(measure)
        try:
            ranking_dict = {
                node: rank for (node, rank) in self.ranking_iter(rank_string)
            }
        except KeyError:
            msg = '{0} has not been ranked'.format(measure)
            raise SonnetException(msg)
        return ranking_dict

    def find_communities(self, min_size=4):
        """
        This method is etremely risky for large dense graphs
        """
        try:
            communities = list(nx.k_clique_communities(self.graph, min_size))
        except nx.NetworkXNotImplemented:
            graph = self.graph.to_undirected()
            communities = list(nx.k_clique_communities(graph, min_size))
        if communities:
            for group, community in enumerate(communities):
                group += 1
                for member in community:
                    self[member]['group'] = group
            for node in self.graph.nodes():
                group = self[node].get('group', '')
                if not group:
                    self[node]['group'] = ''
        else:
            print('No Communities')

    def get_communities(self):
        communities = {}
        try:
            for node, community in self.community_iter():
                if community not in communities:
                    communities[community] = [node]
                else:
                    communities[community].append(node)
        except KeyError:
            print('Finding communities')
            self.find_communities()
            for node, community in self.community_iter():
                if community not in communities:
                    communities[community] = [node]
                else:
                    communities[community].append(node)
        return communities

    def nodes_iter(self):
        return iter(self.graph.node)

    def sonnet_nodes_iter(self):
        for node in self.nodes_iter():
            sonnet_node = {'id': node}
            sonnet_node.update(self[node])
            yield(sonnet_node)

    def attr_iter(self, attr):
        for node in self.nodes_iter():
            yield(node, self[node][attr])

    def sonnet_degree_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['degree'])

    def degree_centrality_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['degree_centrality'])

    def in_degree_centrality_iter(self):
        if not self.graph.is_directed():
            msg = "in_degree_centrality() not defined for undirected graphs."
            raise nx.NetworkXError(msg)
        for node in self.nodes_iter():
            yield(node, self[node]['in_degree_centrality'])

    def out_degree_centrality_iter(self):
        if not self.graph.is_directed():
            msg = "out_degree_centrality() not defined for undirected graphs."
            raise nx.NetworkXError(msg)
        for node in self.nodes_iter():
            yield(node, self[node]['out_degree_centrality'])

    def closeness_centrality_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['closeness_centrality'])

    def betweenness_centrality_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['betweenness_centrality'])

    def eigenvector_centrality_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['eigenvector_centrality'])

    def ranking_iter(self, measure):
        for node in self.nodes_iter():
            yield(node, self[node][measure])

    def community_iter(self):
        for node in self.nodes_iter():
            yield(node, self[node]['group'])

    def jsonify(self):
        graph_data = json_graph.node_link_data(self.graph)
        graph_data['name'] = self.name
        output = json.dumps(graph_data)
        return output


class D3Graph(Sonnet):

    def __init__(self, graph, height=800, width=1280, color_by='community',
                 gravity=0.06, charge=-150, link_distance=40):
        super(D3Graph, self).__init__(
            self,
            name=None,
            min_node_size=1,
            max_node_size=6,
            rank_by='degree_centrality',
            color_by='community'
        )
        self.graph = graph
        self.height = height
        self.width = width
        self.color_by = color_by
        self.gravity = gravity
        self.charge = charge
        self.link_distance = link_distance

    def jsonify(self):
        graph_data = json_graph.node_link_data(self.graph)
        graph_data['name'] = self.name
        graph_data['height'] = self.height
        graph_data['width'] = self.width
        graph_data['color_by'] = self.color_by
        graph_data['gravity'] = self.gravity
        graph_data['charge'] = self.charge
        graph_data['link_distance'] = self.link_distance
        self.graph = json.dumps(graph_data)
        return self.graph
