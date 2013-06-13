""" Partially ordered sort """

from posort.util import reverse_dict

def toposort(edges):
    """ Topological sort algorithm by Kahn [1] - O(nodes + vertices)

    inputs:
        edges - a dict of the form {a: {b, c}} where b and c depend on a
    outputs:
        L - an ordered list of nodes that satisfy the dependencies of edges

    >>> toposort({1: {2, 3}, 2: (3, )})
    [1, 2, 3]

    Closely follows the wikipedia page [2]

    [1] Kahn, Arthur B. (1962), "Topological sorting of large networks",
    Communications of the ACM
    [2] http://en.wikipedia.org/wiki/Toposort#Algorithms
    """
    incoming_edges = reverse_dict(edges)
    incoming_edges = dict((k, set(val)) for k, val in incoming_edges.items())
    S = set((v for v in edges if v not in incoming_edges))
    L = []

    while S:
        n = S.pop()
        L.append(n)
        for m in edges.get(n, ()):
            assert n in incoming_edges[m]
            incoming_edges[m].remove(n)
            if not incoming_edges[m]:
                S.add(m)
    if any(incoming_edges.get(v, None) for v in edges):
        raise ValueError("Input has cycles")
    return L

def posort(l, *cmps):
    """ Partially ordered sort with multiple comparators

    Given a list of comparators order the elements in l so that the comparators
    are satisfied as much as possible giving precedence to earlier comparators.

    inputs:
        l - an iterable of nodes in a graph
        cmps - a sequence of comparator functions that describe which nodes
               should come before which others

    outputs:
        a list of nodes which satisfy the comparators as much as possible.

    >>> lower_tens = lambda a, b: a/10 - b/10 # prefer lower numbers div 10
    >>> prefer evens = lambda a, b: a%2 - b%2 # prefer even numbers
    >>> posort(range(20), lower_tens, prefer_evens)
    [0, 8, 2, 4, 6, 1, 3, 5, 7, 9, 16, 18, 10, 12, 14, 17, 19, 11, 13, 15]

    implemented with toposort """
    comes_before = dict((a, set()) for a in l)
    comes_after  = dict((a, set()) for a in l)

    def add_links(a, b): # b depends on a
        comes_after[a].add(b)
        comes_after[a].update(comes_after[b])
        for c in comes_before[a]:
            comes_after[c].update(comes_after[a])
        comes_before[b].add(a)
        comes_before[b].update(comes_before[a])
        for c in comes_after[b]:
            comes_before[c].update(comes_before[b])

    def check():
        """ Tests for cycles in manufactured edges """
        for a in l:
            for b in l:
                assert not(b in comes_after[a] and a in comes_after[b])

    for cmp in cmps:
        for a in l:
            for b in l:
                if cmp(a, b) < 0: # a wants to come before b
                    # if this wouldn't cause a cycle and isn't already known
                    if not b in comes_before[a] and not b in comes_after[a]:
                        add_links(a, b)
    # check() # debug code

    return toposort(comes_after)
