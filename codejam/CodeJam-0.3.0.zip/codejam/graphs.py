from networkx import *
import itertools as it

def quick_copy(G, include_isolated = True):
    if G.is_directed():
        if G.is_multigraph():
            H = MultiDiGraph()
        else:
            H = DiGraph()
    else:
        if G.is_multigraph():
            H = MultiGraph()
        else:
            H = Graph()

    if ignore_isolated:
        H.add_nodes_from(G.nodes_iter())
    H.add_edges_from(G.edges_iter())

    return H

def bfs(G, n):
    return it.chain([n], (e[1] for e in bfs_edges(G, n)))

def dfs(G, n):
    return dfs_preorder_nodes(G, n)