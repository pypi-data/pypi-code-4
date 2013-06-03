## ***** automatically generated code **** ##
from ndarray.openalea import Factory
if '__all__' not in locals(): __all__ = []

__name__        = 'ndarray.filter'
__version__     = '0.8.0'
__license__     = 'CeCILL-C'
__author__      = ''
__institutes__  = ''
__description__ = ''
__url__         = 'http://openalea.gforge.inria.fr'
__editable__    = 'True'
__icon__        = '/Users/diener/python/ndarray/src/ndarray/icon/cube.png'
__alias__       = []


apply = Factory(name='apply',
                nodeclass='apply',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None},),
                description='\n    Apply a set of standard filter to array data: \n    \n    Call: apply(array-data, <list of key=value arguments>)\n\n    The list of key-value define the filtering to be done and should be given in\n    the order to be process. Possible key-value are:\n    \n      * smooth:  gaussian filtering, value is the sigma parameter (scalar or tuple)\n      * uniform: uniform  filtering (2)\n      * max:     maximum  filtering (1)\n      * min:     minimum  filtering (1)\n      * median:  median   filtering (1)\n      \n      * dilate: grey dilatation (1)\n      * erode:  grey erosion    (1)\n      * close:  grey closing    (1)\n      * open:   grey opening    (1)\n      \n      * linear_map: call linear_map(), value is the tuple (min,max)   (3)\n      * normalize:  call normalize(),  value is the method            (3)\n      * adaptive:   call adaptive(),   value is the sigma             (3)\n      * adaptive_:  call adaptive(),   with uniform kernel            (3)\n          \n    The filtering is done using standard scipy.ndimage functions.\n    \n    (1) The value given (to the key) is the width of the the filter: \n        the distance from the center pixel (the size of the filter is thus 2*value+1)\n        The neighborhood is an (approximated) boolean circle (up to discretization)\n    (2) Same as (*) but the neighborhood is a complete square\n    (3) See doc of respective function\n    ',
                outputs=[{'name': 'filtered_array'}],
                )
__all__.append('apply')

linear_map = Factory(name='linear_map',
                nodeclass='linear_map',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IInt', 'name': 'min', 'value': 0}, {'interface': 'IInt', 'name': 'max', 'value': 1}, {'interface': None, 'name': 'axis', 'value': None}),
                description='\n    mapped_array = linear_map( array, min=0, max=1, axis=None ) \n    \n    Map array values from [array.min(),array.max()] to given [min,max] arguments\n    over the specified axis\n    \n    :Input:\n        array:   array to map from\n        min&max: value to map to\n                 if min (or max) is None, use the array min (or max) \n        axis:   Axis over which the array minimum and maximum are computed. \n                By default `axis` is None, and taken values are for the whole array.\n    \n    :Output:\n        the array with mapped values\n    ',
                outputs=[{'name': 'mapped_array'}],
                )
__all__.append('linear_map')

normalize = Factory(name='normalize',
                nodeclass='normalize',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'method', 'value': 'euclidian'}, {'interface': None, 'name': 'axis', 'value': None}),
                description="\n    normalized_array = normalize(array, method='minmax')\n    \n    normalize array values, following given methods\n    \n    :Input:\n        array:  array to normalize\n        method: either\n                  'minmax':          values are map from array min & max to (0,1)   \n                  'euclidian' or 2:  divide by the euclidian norm   *** default ***\n                  'taxicab'   or 1:  divide by the taxicab   norm\n                   any number p:     divide by the p-norm, i.e. (sum_i(abs(x_i**p))**(1/p)\n        axis:   Axis over which the normalization is done. \n                By default `axis` is None, and it is normalized over the whole array.\n                \n    :Output:\n        the normalized array\n        \n    :Note:\n        For all method but 'minmax', an epsilon value is added to the norm to\n        avoid division by zero.\n      \n    ",
                outputs=[{'name': 'normalized_array'}],
                )
__all__.append('normalize')

adaptive = Factory(name='adaptive',
                nodeclass='adaptive',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'data', 'value': None}, {'interface': None, 'name': 'sigma', 'value': None}, {'interface': 'IStr', 'name': 'kernel', 'value': 'gaussian'}),
                description='\n    Compute adaptive filtering on data:     data - mu(data)\n    \n    Where mu is one of the local-average fonctions (from scipy.ndimage):\n        - gaussian_filter() with sigma as parameter if kernel is \'gaussian\'\n        - uniform_filter()  with sigma use as size parameter if kernel is \'uniform\'\n\n    This is a second-derivative-like filtering that gives a positive values for \n    local maxima (mount) and ridges (crest), and gives negative values for local\n    minima and valley\n    \n    The name "adaptive" is taken from "adaptive thresholding" that apply\n    thresholding on the returned values\n    ',
                outputs=[{'name': 'filtered_data'}],
                )
__all__.append('adaptive')

otsu = Factory(name='otsu',
                nodeclass='otsu',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'step', 'value': 'all'}, {'interface': None, 'name': 'stat', 'value': None}),
                description="\n    Compute the threshold value (with otsu's method) that maximize intra-class inertia \n    \n    Use:    threshold = otsu(array, step='all', stat=None)\n    \n    :Input:\n      array: an nd array\n      step:  either 'all', meaning all possible value\n              or a number, meaning to evenly sample possible values in this number of steps\n              or a 1D list,tuple,array containing the list of values to test\n              ***  if step is not 'all', cells value are considered to be  ***\n              ***     equal to the closest lower value in selected step    *** \n                  \n      stat: If not None, it should be a python list to which is append,\n              the list of tested threshold\n              the intra-class inertia for each threshold values\n              the omega value of the first, then of the second, class\n              the mean (mu) value of the 1st, then 2nd, class (see algorithm description)\n    \n    :Output:\n        threshold: the selected threshold\n    ",
                outputs=[{'name': 'threshold'}],
                )
__all__.append('otsu')

threshold = Factory(name='threshold',
                nodeclass='threshold',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'value', 'value': 'otsu'}),
                description="\n    Basic array thresholding: return array >= value\n    \n    If value is 'otsu' (default), use the threshold computed with otsu's method.\n    ",
                outputs=[{'name': 'mask'}],
                )
__all__.append('threshold')

adaptive_threshold = Factory(name='adaptive_threshold',
                nodeclass='adaptive_threshold',
                nodemodule='ndarray.filter',
                search_path=[],
                inputs=({'interface': None, 'name': 'data', 'value': None}, {'interface': None, 'name': 'sigma', 'value': None}, {'interface': 'IInt', 'name': 'size', 'value': 3}, {'interface': 'IInt', 'name': 'threshold', 'value': 0}),
                description="\n    Compute adaptive thresholding on data\n        data >= mu(data) * (1 + threshold)\n    \n    Where mu is one of the fonctions (from scipy.ndimage):\n        - gaussian_filter() with sigma as parameter    -  if sigma is not None (1st tested option)\n        - uniform_filter()  with size  as parameter    -  otherwise \n        \n    'threshold' can be view as a percentage of strengthening (for positve value) or\n    relaxation (negative) of the inquality thresholding over the local average value (mu)\n    ",
                outputs=[{'name': 'mask'}],
                )
__all__.append('adaptive_threshold')

## ******** end of generated code ******** ##
