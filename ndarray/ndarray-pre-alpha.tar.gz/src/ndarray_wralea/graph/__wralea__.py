## ***** automatically generated code **** ##
from ndarray.openalea import Factory
if '__all__' not in locals(): __all__ = []

__name__        = 'ndarray.graph'
__version__     = '0.8.0'
__license__     = 'CeCILL-C'
__author__      = ''
__institutes__  = ''
__description__ = ''
__url__         = 'http://openalea.gforge.inria.fr'
__editable__    = 'True'
__icon__        = '/Users/diener/python/ndarray/src/ndarray/icon/cube.png'
__alias__       = []


makeDistanceMap = Factory(name='makeDistanceMap',
                nodeclass='makeDistanceMap',
                nodemodule='ndarray.graph',
                search_path=[],
                inputs=({'interface': None, 'name': 'self', 'value': None}, {'interface': 'IStr', 'name': 'method', 'value': 'edges'}),
                description='\n        create distance map used by the shortestPath() method\n        \n        possible method arguments are:\n          \'edges\', uses the edge value created by the the constructor (from footprint)\n          \'nodes\', uses the node value given to the constructor (as node_array)\n           any function that is called with 3 arguments (all with shape nodeNumber x neighborNumber):\n               edges, nodes_source, nodes_destination\n               ex:   lambda E,S,D: E + (S+D)/2     is the edge value + a "node average" distance map\n               \n        Note: element of nodes_destination that are out of the image are equal to np.Inf\n        ',
                outputs=[{'name': 'dmap'}],
                )
__all__.append('makeDistanceMap')

makeArrayGraph = Factory(name='makeArrayGraph',
                nodeclass='makeArrayGraph',
                nodemodule='ndarray.graph',
                search_path=[],
                inputs=({'interface': None, 'name': 'nodes_value', 'value': None}, {'interface': 'IInt', 'name': 'footprint', 'value': 3}),
                description='\n    Graph class designed mostly for ndarray to connect cells to their neighbor. \n    Useful to automatically construct a graph from an array, compute shortest \n    path and distance map. \n    \n    For now, the graph store one value per node (the node-value) and one value \n    per edges, the edge value, which are used to compute distances.\n    See makeDistanceMap()\n    \n    Method list:\n      makeDistanceMap(...)      construct a distance map used by the shortest path\n      shortestPath(...)         compute shortest path map from source points\n      update_shortestPath(...)  update a shortest path\n      getParentMap(...)         get a map of parent indices for each node\n      getPath(...)              retrieve a path -  indices in n-dimension\n      getPath1D(...)            --------------- -  indices in 1-dimension\n    ',
                outputs=[{'name': 'graph'}],
                )
__all__.append('makeArrayGraph')

## ******** end of generated code ******** ##
