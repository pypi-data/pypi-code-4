## ***** automatically generated code **** ##
from ndarray.openalea import Factory
if '__all__' not in locals(): __all__ = []

__name__        = 'ndarray.kernel'
__version__     = '0.8.0'
__license__     = 'CeCILL-C'
__author__      = ''
__institutes__  = ''
__description__ = ''
__url__         = 'http://openalea.gforge.inria.fr'
__editable__    = 'True'
__icon__        = '/Users/diener/python/ndarray/src/ndarray/icon/cube.png'
__alias__       = []


coordinates = Factory(name='coordinates',
                nodeclass='coordinates',
                nodemodule='ndarray.kernel',
                search_path=[],
                inputs=({'interface': None, 'name': 'shape', 'value': None},),
                description="\n    Compute an array containing for each axis the coordinates arrays of given shape:\n        coord = coordinates( shape )\n    \n    \n    :Input:\n        shape: a list/tuple/vector of the kernel sizes of each dimension\n              \n    :Output:\n        A numpy array of shape (N, [shape]) where N is the length of given 'shape'\n        and returned coord[i,:] is the centered coordinates over the ith dimension\n        \n    :Example:\n        coordinates((3,4))\n            array([[[-1, -1, -1, -1],\n                    [ 0,  0,  0,  0],\n                    [ 1,  1,  1,  1]],\n            \n                   [[-1,  0,  1,  2],\n                    [-1,  0,  1,  2],\n                    [-1,  0,  1,  2]]])\n    ",
                outputs=[{'name': 'kernel'}],
                )
__all__.append('coordinates')

distance = Factory(name='distance',
                nodeclass='distance',
                nodemodule='ndarray.kernel',
                search_path=[],
                inputs=({'interface': None, 'name': 'shape', 'value': None}, {'interface': 'IInt', 'name': 'metric', 'value': 2}),
                description="\n    return a distance kernel of given shape:\n        d = distance(shape, metric='euclidian')\n        \n    :Input:\n        shape:  a scalar (for 1d) or list/tuple/vector of the kernel shape\n        metric: the distance function used. Same as the 'method' argument of array.norm()\n        \n    :Output:\n        an array of given shape, where the center cell is zero, and all others\n        have values equal to there distance to this center\n        \n    :Example:\n        distance((3,4))\n            array([[ 1.41,  1. ,  1.4,  2.23],\n                   [ 1.  ,  0. ,  1. ,  2.  ],\n                   [ 1.41,  1. ,  1.4,  2.23]])\n\n    ",
                outputs=[{'name': 'kernel'}],
                )
__all__.append('distance')

ellipse = Factory(name='ellipse',
                nodeclass='ellipse',
                nodemodule='ndarray.kernel',
                search_path=[],
                inputs=({'interface': None, 'name': 'radius', 'value': None}, {'interface': None, 'name': 'shape', 'value': None}),
                description="\n    return a boolean array an ellipse kernel\n        circle = ellipse(shape, radius)\n        \n    :Input:\n        radius: a tuple the ellipse radius for each dimension. \n        shape:  a scalar (for 1d) or list/tuple/vector of the kernel shape\n                *** It must have same length as 'shape' ***\n                By default (if None), the maximum ellipse embedable in 'shape'\n        \n    :Output:\n        an array of given shape, where the pixel inside the ellipse have True value\n        \n    :Example:\n        ellipse((5,9),(2,3)).astype(int)\n            array([[0, 0, 0, 0, 1, 0, 0, 0, 0],\n                   [0, 0, 1, 1, 1, 1, 1, 0, 0],\n                   [0, 1, 1, 1, 1, 1, 1, 1, 0],\n                   [0, 0, 1, 1, 1, 1, 1, 0, 0],\n                   [0, 0, 0, 0, 1, 0, 0, 0, 0]])\n\n    ",
                outputs=[{'name': 'kernel'}],
                )
__all__.append('ellipse')

gaussian = Factory(name='gaussian',
                nodeclass='gaussian',
                nodemodule='ndarray.kernel',
                search_path=[],
                inputs=({'interface': None, 'name': 'sigma', 'value': None}, {'interface': 'ISequence', 'name': 'shape', 'value': []}),
                description='\n    return a gaussian kernel of given shape:\n        d = gaussian(sigma, shape=None)\n        \n    :Input:\n        sigma:  a scalar or list/tuple of the sigma parameter for each dimension\n        shape:  a scalar or list/tuple of the kernel shape\n                if shape size is less than sigma, missing dimension are set to None \n                all None value are replaced to a size determined by sigma\n        \n    :Output:\n        A gaussian kernel of suitable shape. \n        The total sum of all kernel values is equal to 1.\n        \n    :Example:\n        np.round(gaussian((2,3),shape=(4,8)),3)\n        array([[ 0.014,  0.032,  0.053,  0.063,  0.053,  0.032,  0.014,  0.004],\n               [ 0.018,  0.041,  0.068,  0.081,  0.068,  0.041,  0.018,  0.006],\n               [ 0.014,  0.032,  0.053,  0.063,  0.053,  0.032,  0.014,  0.004],\n               [ 0.007,  0.015,  0.025,  0.03 ,  0.025,  0.015,  0.007,  0.002]])\n    ',
                outputs=[{'name': 'kernel'}],
                )
__all__.append('gaussian')

## ******** end of generated code ******** ##
