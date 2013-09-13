# Copyright Matthew Henderson 2013.
# Unknown creation date.
# Last updated: Wed Mar 27 12:27:34 GMT 2013

import networkx

def latin_graph(size):
    """The cartesian product of the complete graph with 'size' vertices with
    itself."""
    K = networkx.complete_graph(size)
    return networkx.cartesian_product(K, K)

def symmetric_latin_graph(size):
    """The graph described on p.20 of 
      "Completing Partial Latin Squares: Cropper's Question"
           by Bobga, Goldwasser, Hilton and Johnson. """
    G = latin_graph(size)
    def V(n):
        return [(i,j) for i in range(n) for j in range(n) if i <= j]
    G2 = G.subgraph(V(size))
    def suitable(v, w): 
        return v[0]<v[1] and v[1]==w[0] and w[0]<w[1]
    for v in G2.nodes():
        for w in G2.nodes():
            if suitable(v,w):
                G2.add_edge(v,w)
    return G2

def rabg(P, r, t, e):
    """The row-absences bipartite-graph of a KF-SPLS."""
    G = networkx.MultiGraph()
    row_indices = range(r)
    row_nodes = ['r' + str(i+1) for i in row_indices]
    symbols = P.symbols()
    symbol_nodes = ['s' + str(i) for i in symbols]
    symbol_nodes_map = dict(zip(symbols, symbol_nodes))
    G.add_nodes_from(row_nodes)
    G.add_nodes_from(symbol_nodes)
    for row in row_indices:
        for symbol in P.row_absences(row):
            G.add_edge(row_nodes[row], symbol_nodes_map[symbol])
    return G

def aram(P, r, t, e):
    """The augmented row-absences multigraph of a KF-SPLS."""
    G = rabg(P, r, t, e)
    return G

