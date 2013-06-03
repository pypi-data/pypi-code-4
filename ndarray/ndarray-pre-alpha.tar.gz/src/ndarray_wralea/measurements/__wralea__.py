## ***** automatically generated code **** ##
from ndarray.openalea import Factory
if '__all__' not in locals(): __all__ = []

__name__        = 'ndarray.measurements'
__version__     = '0.8.0'
__license__     = 'CeCILL-C'
__author__      = ''
__institutes__  = ''
__description__ = ''
__url__         = 'http://openalea.gforge.inria.fr'
__editable__    = 'True'
__icon__        = '/Users/diener/python/ndarray/src/ndarray/icon/cube.png'
__alias__       = []


cluster = Factory(name='cluster',
                nodeclass='cluster',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'method', 'value': 'watershed'}, {'interface': 'IStr', 'name': 'seed', 'value': 'local_min'}, {'interface': 'IInt', 'name': 'seed_min_d', 'value': 1}),
                description=" Segment image in area around selected seeds\n    \n    :Input:\n        array:  The input array to label\n               \n        method: The clustering method. One of:\n                'gradient' - call shortest_path_cluster(...) => require skimage \n                'nearest'  - cluster pixels to closest seed\n                'watershed' (default) - use scipy.ndimage.watershed_ift\n                \n        seed:   The seed to cluster image around. Can be either an interger \n                array where seeds are none zeros cells, or a string indicating \n                which method to use to select seeds. \n                In the later case, the value must be one of the valid 'method' \n                of the find_seed() function\n                - See find_seed() documentation -\n                  \n        seed_min_d: Optional arguments passed to find_seed(...) \n        \n        Other key-value arguments can be given for initial filtering, which are\n        passed to ndarray.filter.apply(...) function. \n        Note that the order in which filters are processed is not garantied\n    \n    :Output:\n        the labeled image, interger array of values in [0,N] \n        the number of segmented area (N)\n       \n       \n    :Example of postprocessing: \n        #To have the minimum, maximum and mean value of label area\n\n        import numpy as np\n        import scipy.ndimage as nd\n    \n        label,N  = label(img) \n        \n        lab_max  = np.array(nd.maximum(img,label,index=np.arange(0,N+1)))\n        lab_min  = np.array(nd.minimum(img,label,index=np.arange(0,N+1)))\n        lab_mean = np.array(nd.mean   (img,label,index=np.arange(0,N+1)))\n        \n        # to get a map of these values onto the labeled area \n        # (eg. for visualisation or further image processing) \n        min_map  = lab_min [label] \n        max_map  = lab_max [label] \n        mean_map = lab_mean[label] \n        \n    See scipy.ndimage for other processing of label map\n    ",
                outputs=[{'name': 'label'}, {'name': 'N'}],
                )
__all__.append('cluster')

find_seed = Factory(name='find_seed',
                nodeclass='find_seed',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'image', 'value': None}, {'interface': 'IStr', 'name': 'method', 'value': 'local_min'}, {'interface': 'IInt', 'name': 'min_distance', 'value': 1}),
                description='\n    Select seed pixels for clustering\n    \n    :Input:\n        image: the nd array to find seed in\n        method: the method use to select seeds. It can be:\n                - local_min: find local minima (default)\n                - extremum:  find local extrema\n                - dist2border: find pixels the further from thresholded gradient norm\n        min_distance: the minimum number of pixel seperating 2 seeds\n        \n        optional key-arguments that is passed to array.filter.apply()\n        \n    :Output:\n        seed_map: an array of same shape as input image, of integer dtype\n                  where background are 0, and seeds are positive integer. A seed\n                  can be several connected pixels. All seeds have different values\n        N: the number of seed found\n        \n    :todo:  \n        extremum is not done yet => mixed of null gradient, null 2nd derivatives\n        pb:     \n    ',
                outputs=[{'name': 'seed'}, {'name': 'N'}],
                )
__all__.append('find_seed')

shortest_path_cluster = Factory(name='shortest_path_cluster',
                nodeclass='shortest_path_cluster',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': None, 'name': 'seed', 'value': None}, {'interface': 'IBool', 'name': 'geometric', 'value': True}),
                description='\n    cluster array cells around seeds such that the connecting path has minimum cost\n    The cost of a path is the sum of the array cells value on the path \n\n    *** This function require the skimage (scikits image) module ***\n\n    :Input:\n        array: float   array containing the cost of each pixels\n        seed:  integer array where 0 are background cells, to cluster around seeds\n               and positive value are clustering seed (the value is the label)\n        geometric: if True, weight diagonal edges by 1/sqrt(2)\n                   - see skimage.graph.MCP and MCP_geometric for details -\n                   \n    :Output:\n        labeled array, i.e. an integer array where each cell has the value\n        of the closest seed\n    ',
                outputs=[{'name': 'labeled_cluster'}],
                )
__all__.append('shortest_path_cluster')

label_dilation = Factory(name='label_dilation',
                nodeclass='label_dilation',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'label', 'value': None}, {'interface': None, 'name': 'distance', 'value': None}, {'interface': 'IStr', 'name': 'metric', 'value': 'chessboard'}),
                description="\n    Dilate labeled area in label array by given distance (in pixels)\n    A label cannot dilate over any other\n        \n    Input:\n        label:    a label array\n        distance: a scalar indicating the euclidian distance\n        metric:   if 'chessbord', use chessbord distance\n                  if 'taxicab',   use taxicap   distance\n                  otherwise,      use euclidian distance (slower)\n    ",
                outputs=[{'name': 'dilated_label'}],
                )
__all__.append('label_dilation')

label_erosion = Factory(name='label_erosion',
                nodeclass='label_erosion',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'label', 'value': None}, {'interface': None, 'name': 'distance', 'value': None}, {'interface': 'IStr', 'name': 'metric', 'value': 'chessboard'}),
                description="\n    Erode labeled area in label array by given distance (in pixels)\n    \n    The erosion is done with respect to background only, not other label. Thus \n    connected label stay connected, if the touching pixels are far enough from\n    the background.\n        \n    Input:\n        label:    a label array\n        distance: a scalar indicating the euclidian distance\n        metric:   if 'chessbord', use chessbord distance\n                  if 'taxicab',   use taxicap   distance\n                  otherwise,      use euclidian distance (slower)\n    ",
                outputs=[{'name': 'closed_label'}],
                )
__all__.append('label_erosion')

label_size = Factory(name='label_size',
                nodeclass='label_size',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'label', 'value': None}, {'interface': None, 'name': 'min_label', 'value': None}),
                description='\n    Number of pixels in each label\n    \n    min_label is the minimum number of label to compute the size of, i.e. the \n    minimum size of the returned array .\n    ',
                outputs=[{'name': 'label_size'}],
                )
__all__.append('label_size')

clean_label = Factory(name='clean_label',
                nodeclass='clean_label',
                nodemodule='ndarray.measurements',
                search_path=[],
                inputs=({'interface': None, 'name': 'label', 'value': None}, {'interface': 'IInt', 'name': 'min_size', 'value': 1}, {'interface': 'IInt', 'name': 'min_dim', 'value': 0}),
                description='\n    remove labeled area that have \n      - a number of pixels less than min_size\n      - both dimension of bounding box less than than min_dim\n    \n    Return:\n      updated label map with contiguous numbering\n    ',
                outputs=[{'name': 'cleaned_label'}],
                )
__all__.append('clean_label')

## ******** end of generated code ******** ##
