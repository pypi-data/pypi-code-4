# sort children based on dependencies

from __future__ import absolute_import
import logging
from pyprotobuf.codegenerator import CodeGenerator

logger = logging.getLogger('pyprotobuf.dependencysorter')

class CycleError(Exception):
    """An exception raised when an unexpected cycle is detected."""
    def __init__(self, nodes):
        self.nodes = nodes

    def __str__(self):
        return 'CycleError: cycle involving: ' + str(self.nodes)

def TopologicallySorted(graph, get_edges):
    """Topologically sort based on a user provided edge definition.

    Args:
      graph: A list of node names.
      get_edges: A function mapping from node name to a hashable collection
                 of node names which this node has outgoing edges to.
    Returns:
      A list containing all of the node in graph in topological order.
      It is assumed that calling get_edges once for each node and caching is
      cheaper than repeatedly calling get_edges.
    Raises:
      CycleError in the event of a cycle.
    Example:
      graph = {'a': '$(b) $(c)', 'b': 'hi', 'c': '$(b)'}
      def GetEdges(node):
        return re.findall(r'\$\(([^))]\)', graph[node])
      print TopologicallySorted(graph.keys(), GetEdges)
      ==>
      ['a', 'c', b']
    """
    visited = set()
    visiting = set()
    ordered_nodes = []

    def Visit(node):
        if node in visiting:
            raise CycleError(visiting)

        if node in visited:
            return

        visited.add(node)
        visiting.add(node)

        for neighbor in get_edges(node):

            # ignore across differing parent boundaries
            if node.parent != neighbor.parent:
                continue

            logger.debug('Node %s requires %s', node, neighbor)
            Visit(neighbor)

        visiting.remove(node)
        ordered_nodes.insert(0, node)

    for node in graph:
        Visit(node)

    return ordered_nodes

def get_edges(node):
    return node.get_dependencies()

def sort_nodes(targets):
    return TopologicallySorted(targets, get_edges)

import pprint
class DependencySorter(CodeGenerator):
    """ Parse the file looking to link together ParseNodes when they refer to each other.
    """

    types = ['bool', 'string', 'int64', 'int32', 'uint64', 'uint32', 'sint64',
    'sint32', 'fixed64', 'fixed32', 'sfixed64', 'sfixed32', 'double', 'float',
    'bytes', 'enum', 'message', 'group']

    logger = logging.getLogger('pyprotobuf.NameResolver')

    def visit_FileNode(self, node):
        # sort the top level messages/enums
        node.children = list(reversed(sort_nodes(node.children)))


    def visit_MessageNode(self, node):
        # sort the top level messages/enums
        node.children = list(reversed(sort_nodes(node.children)))

