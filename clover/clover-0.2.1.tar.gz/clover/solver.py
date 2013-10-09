from __future__ import absolute_import


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
            Visit(neighbor)
            
        visiting.remove(node)
        ordered_nodes.insert(0, node)
      
    for node in graph:
        Visit(node)
        
    return ordered_nodes

def get_edges(node):
    return node.required_sourcefiles
    
def sort_sourcefiles(targets):
    return TopologicallySorted(targets, get_edges)  



class ProvidesMap(object):
    def __init__(self):
        self._map = {}
    
    def add_provide(self, name, source):
        if name in self._map:
            raise MultipleProvideError(name, [self._map[name], source])
            
        self._map[name] = source
    
    def get(self, name):
        return self._map.get(name, None)


    def initialize(self, sources):
        for source in sources:
            for provide_name in source.get_provide_names():
                self.add_provide(provide_name, source)


class Solver(object):
    """Class to represent a full Closure Library dependency tree.

    Offers a queryable tree of dependencies of a given set of sources.  The tree
    will also do logical validation to prevent duplicate provides and circular
    dependencies.
    
     provides_map: Map from namespace to source that provides it.
     
    traversal_path: List of namespaces of our path from the root down the
            dependency/recursion tree.  Used to identify cyclical dependencies.
            This is a list used as a stack -- when the function is entered, the
            current namespace is pushed and popped right before returning.
            Each recursive call will check that the current namespace does not
            appear in the list, throwing a CircularDependencyError if it does.
    """

    def __init__(self, sources):
        """Initializes the tree with a set of sources.
    
        Args:
          sources: A pool of JavaScript sources to calculate dependencies from.
    
        Raises:
          MultipleProvideError: A namespace is provided by muplitple sources.
          NamespaceNotFoundError: A namespace is required but never provided.
        """

        self._sources = sources
        self._provides = ProvidesMap()
        # Ensure nothing was provided twice.
        self._provides.initialize(sources)

    def get_dependencies(self, required_namespaces):
        """Get source dependencies, in order, for the given namespaces.
    
        Args:
          required_namespaces: A string (for one) or list (for one or more) of
            namespaces.
    
        Returns:
          A list of source objects that provide those namespaces and all
          requirements, in dependency order.
    
        Raises:
          NamespaceNotFoundError: A namespace is requested but doesn't exist.
          CircularDependencyError: A cycle is detected in the dependency tree.
        """
        
        
        if isinstance(required_namespaces, str):
            required_namespaces = [required_namespaces]
        
        self.current_deps = []
        self.traversal_path = []
        
        map(self._resolve_dependencies, required_namespaces)
        
        return self.current_deps
        
        
    def sort_deps_list(self, deps):
        def get_node_edges(node):
            requires = map(self._provides.get, node.get_require_names())
            return requires

        deps = list(reversed(sort_sourcefiles(TopologicallySorted(deps, get_node_edges))))
        return deps
        
            
    def _resolve_dependencies(self, required_namespace):
        """Resolve dependencies for Closure source files.
    
        Follows the dependency tree down and builds a list of sources in dependency
        order.  This function will recursively call itself to fill all dependencies
        below the requested namespaces, and then append its sources at the end of
        the list.
    
        Args:
          required_namespace: String of required namespace.
    
        Raises:
          NamespaceNotFoundError: A namespace is requested but doesn't exist.
          CircularDependencyError: A cycle is detected in the dependency tree.
        """
        source = self._provides.get(required_namespace)
        
        if not source:
            raise NamespaceNotFoundError(required_namespace, source)

        if required_namespace in self.traversal_path:
            self.traversal_path.append(required_namespace)  # do this *after* the test

            # This must be a cycle.
            raise CircularDependencyError(self.traversal_path)

        # If we don't have the source yet, we'll have to visit this namespace and
        # add the required dependencies to deps_list.
        if source not in self.current_deps:
            self.traversal_path.append(required_namespace)
            
            # Append all other dependencies before we append our own.
            map(self._resolve_dependencies, source.get_require_names())        
                
            self.current_deps.append(source)

            self.traversal_path.pop()


class SolverError(Exception):
    """Base Solver error."""
    pass


class CircularDependencyError(SolverError):
    """Raised when a dependency cycle is encountered."""

    def __init__(self, dependency_list):
        SolverError.__init__(self)
        self._dependency_list = dependency_list

    def __str__(self):
        return ('Encountered circular dependency:\n%s\n' %
                '\n'.join(self._dependency_list))


class MultipleProvideError(SolverError):
    """Raised when a namespace is provided more than once."""

    def __init__(self, namespace, sources):
        SolverError.__init__(self)
        self._namespace = namespace
        self._sources = sources

    def __str__(self):
        source_strs = map(str, self._sources)

        return ('Namespace "%s" provided more than once in sources:\n%s\n' %
                (self._namespace, '\n'.join(source_strs)))


class NamespaceNotFoundError(SolverError):
    """Raised when a namespace is requested but not provided."""

    def __init__(self, namespace, source=None):
        SolverError.__init__(self)
        self._namespace = namespace
        self._source = source

    def __str__(self):
        msg = 'Namespace "%s" never provided.' % self._namespace
        if self._source:
            msg += ' Required in %s' % self._source
        return msg