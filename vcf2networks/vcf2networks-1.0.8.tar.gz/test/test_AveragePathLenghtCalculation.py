#!/usr/bin/env python
"""
"""
import random
import igraph
from numpy import mean, nan_to_num, nan
from pprint import pprint
import nose
import logging
logging.basicConfig(level=logging.DEBUG)


def get_averagePathLength(mygraph, weight_attribute=False, weighted=False):
    """Calculate the average path lenght of a graph
    
    split_by_component: split calculation by component to speed up computation (not tested) 
    
    See also my gist: https://gist.github.com/4124710
    """
#    return mean( [nan_to_num(m) for m in [mean([len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) <2]) for current_node in mygraph.vs()]   if m >= 0])
    # NOTE: for unconnected components, I need to find a way to calculate the average of the geodesic lengths in the components, as described in igraph.Graph.average_path_length.__elp__
#      calculated
    all_path_lengths = []
    num_path_lengths = 0
    current_lengths = []
    
    if weighted is True and weight_attribute not in mygraph.vs.attributes():
        print("attribute", weight_attribute, "does not exists")
   
    if weighted is True:
        current_lenghts = [path_len for path_len in sum(mygraph.shortest_paths(weights=mygraph.vs()[weight_attribute]), []) if path_len > 0 and path_len != float('inf')]
    else:
#        current_lenghts = [path_len for path_len in sum(mygraph.shortest_paths(), []) if path_len > 0 and path_len != float('inf')]
#        print mygraph.shortest_paths()
#        print (sum(mygraph.shortest_paths(), []))
#        current_lenghts = [path_len for path_len in sum(mygraph.shortest_paths(), []) if path_len > 0 and path_len != float('inf')]
        current_lengths = [path_len for path_len in sum(mygraph.shortest_paths(), []) if path_len > 0 and path_len != float('inf')]
#        print current_lengths

    logging.debug( current_lengths)
    av_path_length = mean(current_lengths)
    return av_path_length

known_cases = {
        'triple_path': {
            'comment': 'graph with a single path, two edges',
            'n_vertices': 3, 'edges': [(0, 1), (1, 2)],
#                              0    1    2
            'expected': mean((1,2, 1,1, 1,2)),
            },
        'quadruple_path': {
            'comment': 'graph with a single path, three edges',
            'n_vertices': 4, 'edges': [(0, 1), (1, 2), (2,3)],
#                               0       1       2       3
            'expected': mean((1,2,3,  1,1,2,  2,1,1,  3,2,1))
            },
        'unconnected_graph': {
            'comment': 'this graph contains unconnected nodes, av.path lenght should be 0 or nan',
            'n_vertices': 5, 'edges': [],
            'expected': nan
            },
        'pairs': {
            'comment': 'network where there are only pairs of edges. Av Path lenght should be 1',
            'n_vertices': 6, 'edges': [(0,1), (2,3), (4,5)],
            'expected': (1 + 1 + 1) / 3.
            },
        'onepair_onecomponent': {
            'comment': 'network with one unconnected node and two connected nodes',
            'n_vertices': 3, 'edges': [(1,2)],
            'expected': 1 
            },
        'onepair_someunconnected': {
            'comment': 'network two connected nodes and some unconnected components, to see the behaviour of the function when there are many unconnected components',
            'n_vertices': 10, 'edges': [(4,6)],
            'expected': 1
            },
        'two_components': {
            'comment': 'two components, each with 2 edges',
            'n_vertices': 10, 'edges': [(0,1), (1,2), (5,6), (6,7)],
#                              0      1      2
            'expected': mean((1,2,   1,1,   1,2)) #* 2 # NOTE: This has the same av.path lenght as triple_path, not the double
            },
        'two_unsymmetric_components1': {
            'comment': 'two components, one with one edge, and one with two', #TODO: finish test case
            'n_vertices': 5, 'edges': [(0,1), (2,3), (3,4)],
#                             0    1     2      3      4 
            'expected': mean((1,   1,   1,2,   1,1,   2,1))
            },
        'two_unsymmetric_components2': {
            'comment': 'two components, one with two edges, and one with three', #TODO: finish test case
            'n_vertices': 10, 'edges': [(0,1), (1,2), (5,6), (6,7), (7,8)],
#                              0      1      2       5        6        7        8
            'expected': mean((1,2,   1,1,   1,2,   1,2,3,   1,1,2,   2,1,1,   3,2,1))
            },
        'problematic1': {
            'comment': 'a graph generated randomly using the Erdos Renyi function, which gives problem because there are too many unconnected nodes',
            'n_vertices': 13,
            'edges':[(1, 4), (3, 7), (6, 10), (5, 11), (8, 11), (6, 12), (11, 12)],
#                             1   3    4         5             6         7         8              10            11             12
            'expected': mean((1,  1,   1,   1,2,2,3,4,     1,1,2,3,3,    1,    1,2,2,3,4,     1,2,3,4,4,    1,1,1,2,3,     1,1,2,2,2))
            },
        'star': {
            'comment': 'a star-like graph',
            'n_vertices': 6,
            'edges':[(1, 3), (2, 3), (3, 4), (3, 5)],
            'expected': mean((1,2,2,2,     2,1,2,2,     1,1,1,1,     2,2,1,2,     2,2,2,1))
            },
        'star_plus_asymmetric': {
            'comment': 'a star-like graph, plus a one-edge component',
            'n_vertices': 10,
            'edges':[(1, 3), (2, 3), (3, 4), (3, 5), (8, 9)],
            'expected': mean((1,2,2,2,     2,1,2,2,     1,1,1,1,     2,2,1,2,      2,2,2,1, 1, 1))
            }
        }
def test_AveragePathLenght_KnownGraph_vs_myimplementation():
    """
    Check if my custom implementation of Average Path Lenght gives the same results as what I calculated manually.
    """
    for (graphname, properties) in known_cases.items():
        mygraph = igraph.Graph()
        mygraph['name'] = graphname
        mygraph['comment'] = properties['comment']
        mygraph.add_vertices(properties['n_vertices'])
        mygraph.add_edges(properties['edges'])
        yield checkPathLenght_Correct_KnownGraph_vs_myimplementation, mygraph, properties['expected']

def checkPathLenght_Correct_KnownGraph_vs_myimplementation(mygraph, expected):
    print(mygraph)
    print(mygraph['name'])
    print(mygraph['comment'])
    print([e.tuple for e in mygraph.es()])
    for p in [mygraph.get_all_shortest_paths(n) for n in mygraph.vs()]: print p
    observed = nan_to_num(get_averagePathLength(mygraph))
    expected = nan_to_num(expected)
    expected_computationally = nan_to_num(mygraph.average_path_length())
    print "my_implementation:", observed, "\nmanual calculation:", expected, "\nigraph.Graph.average_path_lenght:", expected_computationally
    nose.tools.assert_almost_equals(observed, expected)

def test_AveragePathLenght_KnownGraph_vs_igraph():
    """
    Check if my custom implementation of Average Path Lenght gives the same results as the igraph.Graph.average_path_length function.
    """
    for (graphname, properties) in known_cases.items():
        mygraph = igraph.Graph()
        mygraph['name'] = graphname
        mygraph['comment'] = properties['comment']
        mygraph.add_vertices(properties['n_vertices'])
        mygraph.add_edges(properties['edges'])
        yield checkPathLenght_Correct_KnownGraph_vs_igraph, mygraph, properties['expected']

def checkPathLenght_Correct_KnownGraph_vs_igraph(mygraph, expected):
    """
    Check if my custom implementation of Average Path Lenght gives the same results as what I calculated manually.
    """
    print(mygraph)
    print(mygraph['name'])
    print(mygraph['comment'])
    print([e.tuple for e in mygraph.es()])
    for p in [mygraph.get_all_shortest_paths(n) for n in mygraph.vs()]: print p
    observed = nan_to_num(get_averagePathLength(mygraph))
    expected = nan_to_num(expected)
#    mygraph
    expected_computationally = nan_to_num(mygraph.average_path_length())
    print "my_implementation:", observed, "\nmanual calculation:", expected, "\nigraph.Graph.average_path_lenght:", expected_computationally
    for component in mygraph.components():
        subgraph = mygraph.subgraph(component)
        print "subgraph size", subgraph.vcount(), "number edges", subgraph.ecount(), "subgraph average path length:", subgraph.average_path_length()
        print ([[len(node_paths)-1 for node_paths in subgraph.get_shortest_paths(node)] for node in subgraph.vs()])
#    assert False
    nose.tools.assert_almost_equals(observed, expected_computationally)

def test_AveragePathLenght_RandomGraph():
    """Generate some random graphs, and for each of them, check if my implementation of average path lenght gives the same results as the igraph.Graph.average_path_lenght function
    """

    random.seed(10)

    for randomgraph_id in range(10):
        n = random.randrange(2, 20)
#        m = random.randrange(2, (n-1)**2)
        p = random.random()
        yield check_PathLenght_Correct_RandomGraph, n, p

def check_PathLenght_Correct_RandomGraph(nodes, p):
    randomgraph = igraph.Graph.Erdos_Renyi(nodes, p)
    mygraph = randomgraph
    print(randomgraph)
    print randomgraph.get_adjedgelist()
    print [edge.tuple for edge in randomgraph.es]

#    print( "paths", ([[("node ID:", current_node.index, "node paths:", current_node_paths) for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) <2] for current_node in mygraph.vs()]))
    print ([(current_node.index, "paths:", [current_node_paths for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) < 2]) for current_node in mygraph.vs()])
    print
    print "lenght of paths -1", ([(current_node.index, "paths:", [len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) < 2]) for current_node in mygraph.vs()])
    print
    print "mean lenghts -1", ([(current_node.index, "paths:", mean([len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) < 2])) for current_node in mygraph.vs()])
    print "mean lenghts -1", ([mean([len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) < 2]) for current_node in mygraph.vs()])
    print
#    print , ([m for m in [[len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) <2] for current_node in mygraph.vs()]   if m >= 0] )
#    print
    print "mean lenghts -1", (mean( [m for m in [mean([len(current_node_paths)-1 for current_node_paths in mygraph.get_shortest_paths(current_node) if not len(current_node_paths) <2]) for current_node in mygraph.vs()]   if m >= 0] ))
    print
#    pprint (mean( [m for m in [mean([len(p) for p in randomgraph.get_shortest_paths(n) if not len(p) <2]) for n in randomgraph.vs()]   if m >= 0] ))
#    pprint (mean( [m for m in [mean([len(p) for p in randomgraph.get_shortest_paths(n) if not len(p) <2]) for n in randomgraph.vs()]   if m >= 0] ))
#    pprint (mean( [m for m in [mean([len(p) for p in randomgraph.get_shortest_paths(n) if not len(p) <2]) for n in randomgraph.vs()]   if m >= 0] ))

    observed = nan_to_num(get_averagePathLength(randomgraph))
    expected = nan_to_num(randomgraph.average_path_length())
    print observed, expected
#    assert False
    nose.tools.assert_almost_equals(observed, expected)












if __name__ == '__main__':
    pass

