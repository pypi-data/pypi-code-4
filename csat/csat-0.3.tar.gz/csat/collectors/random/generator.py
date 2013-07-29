import random
import math

from csat.graphml.builder import GraphMLDocument, GraphMLWriter


class GraphGenerator(object):
    def __init__(self, domains, nodes, edges, inside_edge_ratio, seed=None):
        self.domains = domains
        self.nodes = nodes
        self.edges = edges
        self.seed = seed
        self.inside_edge_ratio = inside_edge_ratio

    def build_domains(self, graph, domains):
        for i in xrange(domains):
            yield graph.node(i, {
                'domain': 'domain-{}'.format(i)
            }).subgraph()

    def run(self):
        if self.seed is not None:
            random.seed(self.seed)

        doc = GraphMLDocument()

        doc.attr('node', 'domain')
        graph = doc.graph()

        domains = tuple(self.build_domains(graph, self.domains))

        for i in xrange(self.nodes):
            domain_index = random.gauss(len(domains)/2,
                                        math.sqrt(len(domains)))
            domain_index = int(domain_index)
            domain_index = min(domain_index, len(domains) - 1)
            domain_index = max(domain_index, 0)
            domain = domains[domain_index]
            domain.node()

        for i in xrange(self.edges):
            from_domain = to_domain = edge_graph = random.choice(domains)

            if random.random() > self.inside_edge_ratio:
                while to_domain == from_domain:
                    to_domain = random.choice(domains)
                edge_graph = graph

            from_node = random.choice(from_domain.nodes.values())
            to_node = random.choice(to_domain.nodes.values())

            edge_graph.edge(from_node, to_node)

        return GraphMLWriter(doc)
