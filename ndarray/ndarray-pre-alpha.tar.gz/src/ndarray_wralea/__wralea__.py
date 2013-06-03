## ***** automatically generated code **** ##
from ndarray.openalea import Factory
if '__all__' not in locals(): __all__ = []

__name__        = 'ndarray'
__version__     = '0.8.0'
__license__     = 'CeCILL-C'
__author__      = ''
__institutes__  = ''
__description__ = ''
__url__         = 'http://openalea.gforge.inria.fr'
__editable__    = 'True'
__icon__        = '/Users/diener/python/ndarray/src/ndarray/icon/cube.png'
__alias__       = []


asint = Factory(name='asint',
                nodeclass='asint',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'default', 'value': 'int'}, {'interface': 'IInt', 'name': 'minbyte', 'value': 1}, {'interface': 'IBool', 'name': 'u', 'value': True}, {'interface': 'IBool', 'name': 'i', 'value': True}),
                description="\n    return the array unchanged if it is an ndarray of integer dtype, or convert \n    it to 'default' dtype. If array is not an ndarray, convert it.\n    \n    default: the default integer dtype if convertion is needed\n    minbyte: impose a minimum bytes precision\n    u: if True accept unsigned integer dtype\n    i: if True accept   signed integer dtype\n    ",
                outputs=[{'name': 'integer_array'}],
                )
__all__.append('asint')

isint = Factory(name='isint',
                nodeclass='isint',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IBool', 'name': 'u', 'value': True}, {'interface': 'IBool', 'name': 'i', 'value': True}),
                description='\n    Test weither array is of integer dtype.\n    \n    Return False if not integer, of the byte precision (integer) if it is\n    Return False if array is not an ndarray\n    ',
                outputs=[{'name': 'is_integer_array'}],
                )
__all__.append('isint')

asfloat = Factory(name='asfloat',
                nodeclass='asfloat',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IStr', 'name': 'default', 'value': 'float'}, {'interface': 'IInt', 'name': 'minbyte', 'value': 2}),
                description="\n    return the array unchanged if it is an ndarray of float dtype, or convert \n    it to 'default' dtype. If array is not an ndarray, convert it.\n    \n    default: the default float dtype if convertion is needed\n    minbyte: impose a minimum bytes precision (exist in 2,4,8 or 16 bytes precision)\n    ",
                outputs=[{'name': 'float_array'}],
                )
__all__.append('asfloat')

isfloat = Factory(name='isfloat',
                nodeclass='isfloat',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None},),
                description='\n    Test weither array is of float dtype.\n    \n    Return False if not float, of the byte precision (integer) if it is\n    Return False if array is not an ndarray\n    ',
                outputs=[{'name': 'is_float_array'}],
                )
__all__.append('isfloat')

aslice = Factory(name='aslice',
                nodeclass='aslice',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'axis', 'value': None},),
                description='\n    same as slice but return a tuple with None-slice for all preceding axis\n        aslice(axis, [start], stop, [step])\n    ',
                outputs=[{'name': 'axis'}, {'name': 'start'}, {'name': 'stop'}, {'name': 'step'}],
                )
__all__.append('aslice')

norm = Factory(name='norm',
                nodeclass='norm',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IInt', 'name': 'method', 'value': 2}, {'interface': None, 'name': 'axis', 'value': None}, {'interface': 'IBool', 'name': 'squeeze', 'value': True}),
                description="\n    Compute the norm of the input array, following either method\n    \n        larrayl = norm(array, method='euclidian', axis=None, squeeze=True)\n    \n    :Input:\n        array:    elements to compute the norm\n        method:   either\n                    'euclidian' or 2:  the euclidian norm\n                    'taxicab' or 1:    the taxicab   norm\n                     any number p:     the p-norm, i.e. (sum(abs(array**p))**(1/p)\n                  \n        axis:     Axis over which the sum is done. By default `axis` is None,\n                  and all the array elements are summed.\n        squeezed: if axis is not None,\n                  if True, the respective axis of returned array is removed\n                  otherwise, it is it is kept and boradcast\n                \n    :Output:\n        if axis is None, return the total norm of the array values\n        otherwise, return an array with shape equal to the original array shape\n        with the respective axis removed\n\n    ",
                outputs=[{'name': 'norm'}],
                )
__all__.append('norm')

gradient_norm = Factory(name='gradient_norm',
                nodeclass='gradient_norm',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None},),
                description='\n    Compute the norm of gradient of the array: ( sum of squared derivatives )**1/2\n    ',
                outputs=[{'name': 'gradient_norm'}],
                )
__all__.append('gradient_norm')

second_derivatives = Factory(name='second_derivatives',
                nodeclass='second_derivatives',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IInt', 'name': 'smooth', 'value': 2}),
                description="\n    Compute the second derivatives of all dimensions pairs of the input array\n    \n    :Inputs:\n        array:  any ndarray\n        smooth: the second derivative are computed by convolving the input array\n                by [1,-2,1]. The smooth parameter set how many times this basic\n                filter is convoluted with [1,2,1]/2, which smooth it.\n    \n    :Output:\n        Return a tuple of the second derivative arrays in the order (where dd_ij \n        is the the second derivative d2(array)/didj for a N-dimensional array):\n        (dd_00, dd_01, ..., dd_0N, dd_11, dd_12, ..., dd_1N, ..., dd_N-1N, dd_NN)\n\n    :Example:\n       for 3d array 'volume_array'\n       dv_00, dv_01, dv_02, dv_11, dv_12, dv_22 = second_derivatives(volume_array)\n       \n    See also:\n      numpy.gradient    \n    ",
                outputs=[{'name': 'sec_derivatives_list'}],
                )
__all__.append('second_derivatives')

ravel_indices = Factory(name='ravel_indices',
                nodeclass='ravel_indices',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'indices', 'value': None}, {'interface': None, 'name': 'shape', 'value': None}),
                description='\n    Convert nD to 1D indices for an array of given shape.\n        flat_indices = ravel_indices(indices, size)\n    \n    :Input:\n        indices: array of indices. Should be integer and have shape=([S],D), \n                 for S the "subshape" of indices array, pointing to a D dimensional array.\n        shape:   shape of the nd-array these indices are pointing to (a tuple/list/ of length D)\n        \n    :Output: \n        flat_indices: an array of shape S\n    \n    :Note: \n       This is the opposite of unravel_indices: for any tuple \'shape\'\n          ind is equal to    ravel_indices(unravel_indices(ind,shape),shape)\n                   and to  unravel_indices(  ravel_indices(ind,shape),shape)\n    ',
                outputs=[{'name': 'flat_indices'}],
                )
__all__.append('ravel_indices')

unravel_indices = Factory(name='unravel_indices',
                nodeclass='unravel_indices',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'indices', 'value': None}, {'interface': None, 'name': 'shape', 'value': None}),
                description="\n    Convert indices in a flatten array to nD indices of the array with given shape.\n        nd_indices = unravel_indices(indices, shape)\n    \n    :Input:\n        indices: array/list/tuple of flat indices. Should be integer, of any shape S\n        shape:   nD shape of the array these indices are pointing to\n        \n    :Output: \n        nd_indices: a nd-array of shape [S]xK, where \n                    [S] is the shape of indices input argument\n                    and K the size (number of element) of shape     \n    \n    :Note:\n        The algorithm has been inspired from numpy.unravel_index \n        and can be seen as a generalization that manage set of indices\n        However, it does not return tuples and no assertion is done on \n        the input indices before convertion:\n        The output indices might be negative or bigger than the array size\n        \n        This is the opposite of ravel_indices:  for any tuple 'shape'\n          ind is equal to    ravel_indices(unravel_indices(ind,shape),shape)\n                   and to  unravel_indices(  ravel_indices(ind,shape),shape)\n    ",
                outputs=[{'name': 'nD_indices'}],
                )
__all__.append('unravel_indices')

add_dim = Factory(name='add_dim',
                nodeclass='add_dim',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IInt', 'name': 'axis', 'value': -1}, {'interface': 'IInt', 'name': 'size', 'value': 1}, {'interface': 'IInt', 'name': 'shift', 'value': 0}),
                description='\n    Insert a virtual dimension using stride tricks  (i.e. broadcasting)\n    *** The appended dimension is a repeated view over the same data ***\n    \n    call:    new_array = add_dim(array, axis=-1, size=1, shift=0)\n    \n    :Input:\n      - array\n          a numpy ndarray\n      - axis\n          the index of the virtual axis to insert\n          the axis number can be negative. If axis=-n: \n          the added axis is the (array.ndim-n)th dimension of output array\n          (if n=-1, add an axis at the end of input array)\n      - size\n          the number of element this new axis will have\n      - shift\n          (optional) if given, the added dimension becomes a shifted view\n          in the input array. The ith element along the shift dimension \n          start at element i*shift, which should be the index of an element\n          in the given array.\n               \n                               ** warning ** \n            with shift, some valid indices point out of given array memory. \n                 Using it might CRASH PYTHON. Use at your own risk\n                               ** ******* **\n                               \n    :Output:\n        if input array shape is S, the returned array has shape (S[:axis], size, S[axis:])\n        \n    :Example:\n      if A is a has 2x3x4 array, then B = add_dim(A,axis,5) will have shape:\n          - (5,2,3,4)   if   axis= 0\n          - (2,3,5,4)   if   axis= 2\n          - (2,3,4,5)   if   axis= 3 or -1\n      \n      B = add_dim(A,axis=-1,size=1) is the same as B = A[:,:,:,newaxis]\n      \n      B = add_dim(A,axis= 0,size=1) is the same as B = A[newaxis]\n      \n    :Note:\n        The returned array is a (broadcasted) view on the input array. \n        Changing its elements value will affect the original data.\n        \n        With default arguments (axis, size and shift), add_dim add a\n        singleton axis at the end of input array\n    ',
                outputs=[{'name': 'plus1D_array'}],
                )
__all__.append('add_dim')

reshape = Factory(name='reshape',
                nodeclass='reshape',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': None, 'name': 'newshape', 'value': None}, {'interface': 'IStr', 'name': 'order', 'value': 'A'}),
                description="\n    Similar as numpy.reshape but allow to had virtual dimension of size > 1\n    \n    Virtual dimension are indicated by negative value in argument 'newshape'\n    \n    Parameters\n    ----------\n    a : array_like\n        Array to be reshaped.\n    newshape : int or tuple of ints\n        The new shape should be compatible with the original shape. \n        One shape dimension can be None. In this case, the value is inferred\n        from the length of the array and remaining dimensions.\n        Any negative integer means a new dimension with this size. \n    order : {'C', 'F', 'A'}, optional\n        Determines whether the array data should be viewed as in C\n        (row-major) order, FORTRAN (column-major) order, or the C/FORTRAN\n        order should be preserved.\n    \n    Returns\n    -------\n    reshaped_array : a view on input array if possible, otherwise a copy.\n    \n    See Also\n    --------\n    numpy.reshape\n    \n    Example:\n    --------\n        A = np.arange(12).reshape((3,4))\n        print A\n            [[ 0,  1,  2,  3],\n             [ 4,  5,  6,  7],\n             [ 8,  9, 10, 11]]\n        B = reshape(A,(2,-3,None))\n        print B.shape\n            (2, 3, 6)\n        # second dimension of B is virtual:\n        B[1,1,1] = 42\n        print B\n            [[[ 0  1  2  3  4  5]\n              [ 0  1  2  3  4  5]\n              [ 0  1  2  3  4  5]]\n            \n             [[ 6 42  8  9 10 11]\n              [ 6 42  8  9 10 11]\n              [ 6 42  8  9 10 11]]]\n              \n    *** Warning: the order option has not been tested *** \n    ",
                outputs=[{'name': 'reshaped_array'}],
                )
__all__.append('reshape')

pad_array = Factory(name='pad_array',
                nodeclass='pad_array',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': None, 'name': 'low_pad', 'value': None}, {'interface': None, 'name': 'high_pad', 'value': None}, {'interface': 'IInt', 'name': 'fill_value', 'value': 0}),
                description="\n    Returned a copy of input array with increased shape\n    \n    :Input:\n      array:      input data\n      low_pad:    the number of elements to add before each dimension  (*)\n      high_pad:   the number of elements to add after  each dimension  (*)\n      fill_value: either the value to put in added array elements (default=0)\n                  or 'nearest' to fill with the value of the nearest input data\n      \n    (*) can be either a single number, in which case it applies to all dimensions, \n        or a tuple/list/array with length less or equal to array dimension. \n        If less, the (preceeding) missing value are set to 0\n        In all cases, the values are rounded to the nearest integers\n        \n    :Output:\n      The returned array has shape = input array shape + |low_pad| + |high_pad|\n      and same dtype as input array\n      \n    :Note:\n      the input array data is contained in the returned array, \n      starting at position |low_pad|\n      \n    :Example:\n      In:   pad_array(np.arange(6).reshape(2,3)+10, 1, (1,3), fill_value=-1)\n      Out:  array([[-1, -1, -1, -1, -1, -1, -1],\n                   [-1, 10, 11, 12, -1, -1, -1],\n                   [-1, 13, 14, 15, -1, -1, -1],\n                   [-1, -1, -1, -1, -1, -1, -1]])\n    ",
                outputs=[{'name': 'padded_array'}],
                )
__all__.append('pad_array')

local_min = Factory(name='local_min',
                nodeclass='local_min',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'array', 'value': None}, {'interface': 'IInt', 'name': 'footprint', 'value': 3}, {'interface': None, 'name': 'mask', 'value': None}, {'interface': 'IBool', 'name': 'strict', 'value': False}, {'interface': 'IBool', 'name': 'return_indices', 'value': False}),
                description="\n    Detects the local minima of the given array using the local minimum scipy filter.\n\n    'footprint' defined the neighborhood of each array cell. \n    If it is a scalar, use a window of this size in all dimension\n    if it is a list or tuple of length equal to the array rank, each element \n    define the window size in each dimension\n    Otherwise it must be a numpy array of same rank as input array\n    \n    If 'mask' is not None, its zero (or False) valued entries are considered invalid  \n\n    if 'strict' is False (default) an array element is considered a local minima \n    if it is less or equal to all its neighbors. It can result in the selection\n    of whole minimal plateau (connected area where pixels have the same value).\n    Otherwise, some noise is added to select unconnected local minima.\n    \n    If 'return_indices' is True,  it returns a list of 2 lists:\n    the 1st containing the x et the 2nd the y coordinates of all local minima.\n    => Use zip(*local_min(...)) to get list of (x,y) tuples \n    \n    This function has been strongly inspired by\n      http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710\n    ",
                outputs=[{'name': 'local_min'}],
                )
__all__.append('local_min')

fill = Factory(name='fill',
                nodeclass='fill',
                nodemodule='ndarray',
                search_path=[],
                inputs=({'interface': None, 'name': 'data', 'value': None}, {'interface': None, 'name': 'invalid', 'value': None}, {'interface': 'IInt', 'name': 'max_distance', 'value': -1}),
                description="\n    Replace the value of invalid 'data' cells (indicated by 'invalid') \n    by the value of the nearest valid data cell\n    \n    Input:\n        data:    numpy array of any dimension\n        invalid: a binary array of same shape as 'data'. \n                 True cells indicate where data value should be filled (replaced)\n                  => If None (default), use: invalid  = np.isnan(data)\n        max_distance: distance up to which cells are filled. If negative, no limit. \n               \n    Output: \n        Return a filled array. \n    ",
                outputs=[{'name': 'filled_array'}],
                )
__all__.append('fill')

## ******** end of generated code ******** ##
