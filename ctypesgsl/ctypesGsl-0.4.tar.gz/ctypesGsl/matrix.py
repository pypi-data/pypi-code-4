### automatically generated, do not edit by hand

from ctypes import c_char, c_int, c_uint, c_long, c_ulong, c_short, c_ushort
from ctypes import c_float, c_double
from ctypes import POINTER
from cgsl_complex import gsl_complex, gsl_complex_float
try:
    from ctypes import c_ubyte
except:
    pass
try:
    from ctypes import c_longdouble
except:
    pass

from utils import *
from utils import _set_types
from utils import _gsl_check_status, _gsl_check_null_pointer
from utils import _int_to_bool

from block import *

from vector import *

from matrix_base import *


class gsl_matrix(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_double)),
                ('block',  POINTER(gsl_block)),
                ('owner',  c_int)]
class gsl_matrix_view(Structure):
    _fields_ = [('matrix', gsl_matrix)]

_set_types('matrix_alloc', POINTER(gsl_matrix), [c_size_t, c_size_t])
_set_types('matrix_free', None, [POINTER(gsl_matrix)])
_set_types('matrix_get', c_double, [POINTER(gsl_matrix), c_size_t, c_size_t])
_set_types('matrix_set', None, [POINTER(gsl_matrix), c_size_t, c_size_t, c_double])

_set_types('matrix_set_all',   None, [POINTER(gsl_matrix), c_double])
_set_types('matrix_set_zero',  None, [POINTER(gsl_matrix)])
_set_types('matrix_set_identity', None, [POINTER(gsl_matrix)])

_set_types('matrix_submatrix', gsl_matrix_view,
           [POINTER(gsl_matrix),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_row', gsl_vector_view, [POINTER(gsl_matrix), c_size_t])
_set_types('matrix_column', gsl_vector_view, [POINTER(gsl_matrix), c_size_t])
_set_types('matrix_diagonal', gsl_vector_view, [POINTER(gsl_matrix)])
_set_types('matrix_subdiagonal', gsl_vector_view, [POINTER(gsl_matrix), c_size_t])
_set_types('matrix_superdiagonal', gsl_vector_view, [POINTER(gsl_matrix), c_size_t])


_set_types('matrix_memcpy', _gsl_check_status, [POINTER(gsl_matrix),
                                                        POINTER(gsl_matrix)])
_set_types('matrix_swap',   _gsl_check_status, [POINTER(gsl_matrix),
                                                        POINTER(gsl_matrix)])

_set_types('matrix_get_row', _gsl_check_status, [POINTER(gsl_vector),
                                                         POINTER(gsl_matrix), c_size_t])
_set_types('matrix_get_col', _gsl_check_status, [POINTER(gsl_vector),
                                                         POINTER(gsl_matrix), c_size_t])
_set_types('matrix_set_row', _gsl_check_status, [POINTER(gsl_matrix), c_size_t,
                                                         POINTER(gsl_vector)])
_set_types('matrix_set_col', _gsl_check_status, [POINTER(gsl_matrix), c_size_t,
                                                         POINTER(gsl_vector)])

_set_types('matrix_swap_rows', _gsl_check_status, [POINTER(gsl_matrix), c_size_t, c_size_t])
_set_types('matrix_swap_columns', _gsl_check_status, [POINTER(gsl_matrix), c_size_t, c_size_t])
_set_types('matrix_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix), c_size_t, c_size_t])

_set_types('matrix_transpose', _gsl_check_status, [POINTER(gsl_matrix)])
_set_types('matrix_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix),
                                                                  POINTER(gsl_matrix)])



_set_types('matrix_add', _gsl_check_status, [POINTER(gsl_matrix),
                                                     POINTER(gsl_matrix)])
_set_types('matrix_sub', _gsl_check_status, [POINTER(gsl_matrix),
                                                     POINTER(gsl_matrix)])
_set_types('matrix_mul_elements', _gsl_check_status, [POINTER(gsl_matrix),
                                                              POINTER(gsl_matrix)])
_set_types('matrix_div_elements', _gsl_check_status, [POINTER(gsl_matrix),
                                                              POINTER(gsl_matrix)])


_set_types('matrix_scale', _gsl_check_status, [POINTER(gsl_matrix),
                                                       c_double])
_set_types('matrix_add_constant', _gsl_check_status, [POINTER(gsl_matrix),
                                                              c_double])



_set_types('matrix_max', c_double, [POINTER(gsl_matrix)])
_set_types('matrix_min', c_double, [POINTER(gsl_matrix)])
_set_types('matrix_minmax', None, [POINTER(gsl_matrix),
                                           POINTER(c_double), POINTER(c_double)])
_set_types('matrix_max_index', None, [POINTER(gsl_matrix),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_min_index', None, [POINTER(gsl_matrix),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_minmax_index', None, [POINTER(gsl_matrix),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_isnull', _int_to_bool, [POINTER(gsl_matrix)])

#_set_types('matrix_ispos', _int_to_bool, [POINTER(gsl_matrix)])
#_set_types('matrix_isneg', _int_to_bool, [POINTER(gsl_matrix)])




class matrix(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix):
                libgsl.gsl_matrix_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_row(self.ptr, i)
        return vector_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_column(self.ptr, j)
        return vector_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_superdiagonal(self.ptr, k)
        return vector_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_subdiagonal(self.ptr, k)
        return vector_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_superdiagonal(self.ptr, k)
        return vector_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix(*self.shape)
        libgsl.gsl_matrix_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    
    def __iadd__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_add_constant(self.ptr, other)
        else:
            libgsl.gsl_matrix_add(self.ptr, other.ptr)
        return self
    def __isub__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_add_constant(self.ptr, -other)
        else:
            libgsl.gsl_matrix_sub(self.ptr, other.ptr)
        return self
    def __imul__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_scale(self.ptr, other)
        else:
            libgsl.gsl_matrix_mul_elements(self.ptr, other.ptr)
        return self
    def __idiv__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_scale(self.ptr, 1.0 / other)
        else:
            libgsl.gsl_matrix_div_elements(self.ptr, other.ptr)
        return self
    

    
    def max(self):
        return libgsl.gsl_matrix_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_min(self.ptr)
    def minmax(self):
        r1 = c_double()
        r2 = c_double()
        libgsl.gsl_matrix_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_isneg(self.ptr)
    



class matrix_view(matrix):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_view_from_gsl(matrix):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_float(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_float)),
                ('block',  POINTER(gsl_block_float)),
                ('owner',  c_int)]
class gsl_matrix_float_view(Structure):
    _fields_ = [('matrix', gsl_matrix_float)]

_set_types('matrix_float_alloc', POINTER(gsl_matrix_float), [c_size_t, c_size_t])
_set_types('matrix_float_free', None, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_get', c_float, [POINTER(gsl_matrix_float), c_size_t, c_size_t])
_set_types('matrix_float_set', None, [POINTER(gsl_matrix_float), c_size_t, c_size_t, c_float])

_set_types('matrix_float_set_all',   None, [POINTER(gsl_matrix_float), c_float])
_set_types('matrix_float_set_zero',  None, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_set_identity', None, [POINTER(gsl_matrix_float)])

_set_types('matrix_float_submatrix', gsl_matrix_float_view,
           [POINTER(gsl_matrix_float),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_float_row', gsl_vector_float_view, [POINTER(gsl_matrix_float), c_size_t])
_set_types('matrix_float_column', gsl_vector_float_view, [POINTER(gsl_matrix_float), c_size_t])
_set_types('matrix_float_diagonal', gsl_vector_float_view, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_subdiagonal', gsl_vector_float_view, [POINTER(gsl_matrix_float), c_size_t])
_set_types('matrix_float_superdiagonal', gsl_vector_float_view, [POINTER(gsl_matrix_float), c_size_t])


_set_types('matrix_float_memcpy', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                        POINTER(gsl_matrix_float)])
_set_types('matrix_float_swap',   _gsl_check_status, [POINTER(gsl_matrix_float),
                                                        POINTER(gsl_matrix_float)])

_set_types('matrix_float_get_row', _gsl_check_status, [POINTER(gsl_vector_float),
                                                         POINTER(gsl_matrix_float), c_size_t])
_set_types('matrix_float_get_col', _gsl_check_status, [POINTER(gsl_vector_float),
                                                         POINTER(gsl_matrix_float), c_size_t])
_set_types('matrix_float_set_row', _gsl_check_status, [POINTER(gsl_matrix_float), c_size_t,
                                                         POINTER(gsl_vector_float)])
_set_types('matrix_float_set_col', _gsl_check_status, [POINTER(gsl_matrix_float), c_size_t,
                                                         POINTER(gsl_vector_float)])

_set_types('matrix_float_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_float), c_size_t, c_size_t])
_set_types('matrix_float_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_float), c_size_t, c_size_t])
_set_types('matrix_float_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_float), c_size_t, c_size_t])

_set_types('matrix_float_transpose', _gsl_check_status, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                                  POINTER(gsl_matrix_float)])



_set_types('matrix_float_add', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                     POINTER(gsl_matrix_float)])
_set_types('matrix_float_sub', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                     POINTER(gsl_matrix_float)])
_set_types('matrix_float_mul_elements', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                              POINTER(gsl_matrix_float)])
_set_types('matrix_float_div_elements', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                              POINTER(gsl_matrix_float)])


_set_types('matrix_float_scale', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                       c_double])
_set_types('matrix_float_add_constant', _gsl_check_status, [POINTER(gsl_matrix_float),
                                                              c_double])



_set_types('matrix_float_max', c_float, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_min', c_float, [POINTER(gsl_matrix_float)])
_set_types('matrix_float_minmax', None, [POINTER(gsl_matrix_float),
                                           POINTER(c_float), POINTER(c_float)])
_set_types('matrix_float_max_index', None, [POINTER(gsl_matrix_float),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_float_min_index', None, [POINTER(gsl_matrix_float),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_float_minmax_index', None, [POINTER(gsl_matrix_float),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_float_isnull', _int_to_bool, [POINTER(gsl_matrix_float)])

#_set_types('matrix_float_ispos', _int_to_bool, [POINTER(gsl_matrix_float)])
#_set_types('matrix_float_isneg', _int_to_bool, [POINTER(gsl_matrix_float)])




class matrix_float(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_float_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_float):
                libgsl.gsl_matrix_float_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_float_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_float_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_float_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_float_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_float_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_float_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_float_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_float_row(self.ptr, i)
        return vector_float_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_float_column(self.ptr, j)
        return vector_float_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_float_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_float_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_float_superdiagonal(self.ptr, k)
        return vector_float_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_float_subdiagonal(self.ptr, k)
        return vector_float_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_float_superdiagonal(self.ptr, k)
        return vector_float_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_float(*self.shape)
        libgsl.gsl_matrix_float_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_float_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_float_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_float_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_float_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_float_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_float_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_float_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_float_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_float_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_float(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_float_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    
    def __iadd__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_float_add_constant(self.ptr, other)
        else:
            libgsl.gsl_matrix_float_add(self.ptr, other.ptr)
        return self
    def __isub__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_float_add_constant(self.ptr, -other)
        else:
            libgsl.gsl_matrix_float_sub(self.ptr, other.ptr)
        return self
    def __imul__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_float_scale(self.ptr, other)
        else:
            libgsl.gsl_matrix_float_mul_elements(self.ptr, other.ptr)
        return self
    def __idiv__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_matrix_float_scale(self.ptr, 1.0 / other)
        else:
            libgsl.gsl_matrix_float_div_elements(self.ptr, other.ptr)
        return self
    

    
    def max(self):
        return libgsl.gsl_matrix_float_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_float_min(self.ptr)
    def minmax(self):
        r1 = c_float()
        r2 = c_float()
        libgsl.gsl_matrix_float_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_float_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_float_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_float_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_float_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_float_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_float_isneg(self.ptr)
    



class matrix_float_view(matrix_float):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_float_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_float))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_float_view_from_gsl(matrix_float):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_int(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_int)),
                ('block',  POINTER(gsl_block_int)),
                ('owner',  c_int)]
class gsl_matrix_int_view(Structure):
    _fields_ = [('matrix', gsl_matrix_int)]

_set_types('matrix_int_alloc', POINTER(gsl_matrix_int), [c_size_t, c_size_t])
_set_types('matrix_int_free', None, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_get', c_int, [POINTER(gsl_matrix_int), c_size_t, c_size_t])
_set_types('matrix_int_set', None, [POINTER(gsl_matrix_int), c_size_t, c_size_t, c_int])

_set_types('matrix_int_set_all',   None, [POINTER(gsl_matrix_int), c_int])
_set_types('matrix_int_set_zero',  None, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_set_identity', None, [POINTER(gsl_matrix_int)])

_set_types('matrix_int_submatrix', gsl_matrix_int_view,
           [POINTER(gsl_matrix_int),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_int_row', gsl_vector_int_view, [POINTER(gsl_matrix_int), c_size_t])
_set_types('matrix_int_column', gsl_vector_int_view, [POINTER(gsl_matrix_int), c_size_t])
_set_types('matrix_int_diagonal', gsl_vector_int_view, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_subdiagonal', gsl_vector_int_view, [POINTER(gsl_matrix_int), c_size_t])
_set_types('matrix_int_superdiagonal', gsl_vector_int_view, [POINTER(gsl_matrix_int), c_size_t])


_set_types('matrix_int_memcpy', _gsl_check_status, [POINTER(gsl_matrix_int),
                                                        POINTER(gsl_matrix_int)])
_set_types('matrix_int_swap',   _gsl_check_status, [POINTER(gsl_matrix_int),
                                                        POINTER(gsl_matrix_int)])

_set_types('matrix_int_get_row', _gsl_check_status, [POINTER(gsl_vector_int),
                                                         POINTER(gsl_matrix_int), c_size_t])
_set_types('matrix_int_get_col', _gsl_check_status, [POINTER(gsl_vector_int),
                                                         POINTER(gsl_matrix_int), c_size_t])
_set_types('matrix_int_set_row', _gsl_check_status, [POINTER(gsl_matrix_int), c_size_t,
                                                         POINTER(gsl_vector_int)])
_set_types('matrix_int_set_col', _gsl_check_status, [POINTER(gsl_matrix_int), c_size_t,
                                                         POINTER(gsl_vector_int)])

_set_types('matrix_int_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_int), c_size_t, c_size_t])
_set_types('matrix_int_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_int), c_size_t, c_size_t])
_set_types('matrix_int_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_int), c_size_t, c_size_t])

_set_types('matrix_int_transpose', _gsl_check_status, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_int),
                                                                  POINTER(gsl_matrix_int)])






_set_types('matrix_int_max', c_int, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_min', c_int, [POINTER(gsl_matrix_int)])
_set_types('matrix_int_minmax', None, [POINTER(gsl_matrix_int),
                                           POINTER(c_int), POINTER(c_int)])
_set_types('matrix_int_max_index', None, [POINTER(gsl_matrix_int),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_int_min_index', None, [POINTER(gsl_matrix_int),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_int_minmax_index', None, [POINTER(gsl_matrix_int),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_int_isnull', _int_to_bool, [POINTER(gsl_matrix_int)])

#_set_types('matrix_int_ispos', _int_to_bool, [POINTER(gsl_matrix_int)])
#_set_types('matrix_int_isneg', _int_to_bool, [POINTER(gsl_matrix_int)])




class matrix_int(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_int_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_int):
                libgsl.gsl_matrix_int_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_int_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_int_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_int_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_int_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_int_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_int_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_int_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_int_row(self.ptr, i)
        return vector_int_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_int_column(self.ptr, j)
        return vector_int_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_int_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_int_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_int_superdiagonal(self.ptr, k)
        return vector_int_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_int_subdiagonal(self.ptr, k)
        return vector_int_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_int_superdiagonal(self.ptr, k)
        return vector_int_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_int(*self.shape)
        libgsl.gsl_matrix_int_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_int_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_int_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_int_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_int_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_int_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_int_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_int_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_int_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_int_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_int(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_int_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_int_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_int_min(self.ptr)
    def minmax(self):
        r1 = c_int()
        r2 = c_int()
        libgsl.gsl_matrix_int_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_int_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_int_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_int_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_int_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_int_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_int_isneg(self.ptr)
    



class matrix_int_view(matrix_int):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_int_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_int))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_int_view_from_gsl(matrix_int):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_uint(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_uint)),
                ('block',  POINTER(gsl_block_uint)),
                ('owner',  c_int)]
class gsl_matrix_uint_view(Structure):
    _fields_ = [('matrix', gsl_matrix_uint)]

_set_types('matrix_uint_alloc', POINTER(gsl_matrix_uint), [c_size_t, c_size_t])
_set_types('matrix_uint_free', None, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_get', c_uint, [POINTER(gsl_matrix_uint), c_size_t, c_size_t])
_set_types('matrix_uint_set', None, [POINTER(gsl_matrix_uint), c_size_t, c_size_t, c_uint])

_set_types('matrix_uint_set_all',   None, [POINTER(gsl_matrix_uint), c_uint])
_set_types('matrix_uint_set_zero',  None, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_set_identity', None, [POINTER(gsl_matrix_uint)])

_set_types('matrix_uint_submatrix', gsl_matrix_uint_view,
           [POINTER(gsl_matrix_uint),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_uint_row', gsl_vector_uint_view, [POINTER(gsl_matrix_uint), c_size_t])
_set_types('matrix_uint_column', gsl_vector_uint_view, [POINTER(gsl_matrix_uint), c_size_t])
_set_types('matrix_uint_diagonal', gsl_vector_uint_view, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_subdiagonal', gsl_vector_uint_view, [POINTER(gsl_matrix_uint), c_size_t])
_set_types('matrix_uint_superdiagonal', gsl_vector_uint_view, [POINTER(gsl_matrix_uint), c_size_t])


_set_types('matrix_uint_memcpy', _gsl_check_status, [POINTER(gsl_matrix_uint),
                                                        POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_swap',   _gsl_check_status, [POINTER(gsl_matrix_uint),
                                                        POINTER(gsl_matrix_uint)])

_set_types('matrix_uint_get_row', _gsl_check_status, [POINTER(gsl_vector_uint),
                                                         POINTER(gsl_matrix_uint), c_size_t])
_set_types('matrix_uint_get_col', _gsl_check_status, [POINTER(gsl_vector_uint),
                                                         POINTER(gsl_matrix_uint), c_size_t])
_set_types('matrix_uint_set_row', _gsl_check_status, [POINTER(gsl_matrix_uint), c_size_t,
                                                         POINTER(gsl_vector_uint)])
_set_types('matrix_uint_set_col', _gsl_check_status, [POINTER(gsl_matrix_uint), c_size_t,
                                                         POINTER(gsl_vector_uint)])

_set_types('matrix_uint_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_uint), c_size_t, c_size_t])
_set_types('matrix_uint_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_uint), c_size_t, c_size_t])
_set_types('matrix_uint_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_uint), c_size_t, c_size_t])

_set_types('matrix_uint_transpose', _gsl_check_status, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_uint),
                                                                  POINTER(gsl_matrix_uint)])






_set_types('matrix_uint_max', c_uint, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_min', c_uint, [POINTER(gsl_matrix_uint)])
_set_types('matrix_uint_minmax', None, [POINTER(gsl_matrix_uint),
                                           POINTER(c_uint), POINTER(c_uint)])
_set_types('matrix_uint_max_index', None, [POINTER(gsl_matrix_uint),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_uint_min_index', None, [POINTER(gsl_matrix_uint),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_uint_minmax_index', None, [POINTER(gsl_matrix_uint),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_uint_isnull', _int_to_bool, [POINTER(gsl_matrix_uint)])




class matrix_uint(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_uint_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_uint):
                libgsl.gsl_matrix_uint_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_uint_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_uint_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_uint_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_uint_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_uint_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_uint_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_uint_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_uint_row(self.ptr, i)
        return vector_uint_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_uint_column(self.ptr, j)
        return vector_uint_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_uint_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_uint_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_uint_superdiagonal(self.ptr, k)
        return vector_uint_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_uint_subdiagonal(self.ptr, k)
        return vector_uint_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_uint_superdiagonal(self.ptr, k)
        return vector_uint_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_uint(*self.shape)
        libgsl.gsl_matrix_uint_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_uint_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_uint_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_uint_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_uint_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_uint_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_uint_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_uint_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_uint_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_uint_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_uint(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_uint_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_uint_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_uint_min(self.ptr)
    def minmax(self):
        r1 = c_uint()
        r2 = c_uint()
        libgsl.gsl_matrix_uint_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_uint_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_uint_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_uint_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_uint_isnull(self.ptr)
    



class matrix_uint_view(matrix_uint):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_uint_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_uint))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_uint_view_from_gsl(matrix_uint):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_long(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_long)),
                ('block',  POINTER(gsl_block_long)),
                ('owner',  c_int)]
class gsl_matrix_long_view(Structure):
    _fields_ = [('matrix', gsl_matrix_long)]

_set_types('matrix_long_alloc', POINTER(gsl_matrix_long), [c_size_t, c_size_t])
_set_types('matrix_long_free', None, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_get', c_long, [POINTER(gsl_matrix_long), c_size_t, c_size_t])
_set_types('matrix_long_set', None, [POINTER(gsl_matrix_long), c_size_t, c_size_t, c_long])

_set_types('matrix_long_set_all',   None, [POINTER(gsl_matrix_long), c_long])
_set_types('matrix_long_set_zero',  None, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_set_identity', None, [POINTER(gsl_matrix_long)])

_set_types('matrix_long_submatrix', gsl_matrix_long_view,
           [POINTER(gsl_matrix_long),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_long_row', gsl_vector_long_view, [POINTER(gsl_matrix_long), c_size_t])
_set_types('matrix_long_column', gsl_vector_long_view, [POINTER(gsl_matrix_long), c_size_t])
_set_types('matrix_long_diagonal', gsl_vector_long_view, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_subdiagonal', gsl_vector_long_view, [POINTER(gsl_matrix_long), c_size_t])
_set_types('matrix_long_superdiagonal', gsl_vector_long_view, [POINTER(gsl_matrix_long), c_size_t])


_set_types('matrix_long_memcpy', _gsl_check_status, [POINTER(gsl_matrix_long),
                                                        POINTER(gsl_matrix_long)])
_set_types('matrix_long_swap',   _gsl_check_status, [POINTER(gsl_matrix_long),
                                                        POINTER(gsl_matrix_long)])

_set_types('matrix_long_get_row', _gsl_check_status, [POINTER(gsl_vector_long),
                                                         POINTER(gsl_matrix_long), c_size_t])
_set_types('matrix_long_get_col', _gsl_check_status, [POINTER(gsl_vector_long),
                                                         POINTER(gsl_matrix_long), c_size_t])
_set_types('matrix_long_set_row', _gsl_check_status, [POINTER(gsl_matrix_long), c_size_t,
                                                         POINTER(gsl_vector_long)])
_set_types('matrix_long_set_col', _gsl_check_status, [POINTER(gsl_matrix_long), c_size_t,
                                                         POINTER(gsl_vector_long)])

_set_types('matrix_long_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_long), c_size_t, c_size_t])
_set_types('matrix_long_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_long), c_size_t, c_size_t])
_set_types('matrix_long_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_long), c_size_t, c_size_t])

_set_types('matrix_long_transpose', _gsl_check_status, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_long),
                                                                  POINTER(gsl_matrix_long)])






_set_types('matrix_long_max', c_long, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_min', c_long, [POINTER(gsl_matrix_long)])
_set_types('matrix_long_minmax', None, [POINTER(gsl_matrix_long),
                                           POINTER(c_long), POINTER(c_long)])
_set_types('matrix_long_max_index', None, [POINTER(gsl_matrix_long),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_long_min_index', None, [POINTER(gsl_matrix_long),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_long_minmax_index', None, [POINTER(gsl_matrix_long),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_long_isnull', _int_to_bool, [POINTER(gsl_matrix_long)])

#_set_types('matrix_long_ispos', _int_to_bool, [POINTER(gsl_matrix_long)])
#_set_types('matrix_long_isneg', _int_to_bool, [POINTER(gsl_matrix_long)])




class matrix_long(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_long_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_long):
                libgsl.gsl_matrix_long_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_long_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_long_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_long_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_long_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_long_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_long_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_long_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_long_row(self.ptr, i)
        return vector_long_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_long_column(self.ptr, j)
        return vector_long_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_long_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_long_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_long_superdiagonal(self.ptr, k)
        return vector_long_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_long_subdiagonal(self.ptr, k)
        return vector_long_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_long_superdiagonal(self.ptr, k)
        return vector_long_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_long(*self.shape)
        libgsl.gsl_matrix_long_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_long_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_long_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_long_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_long_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_long_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_long_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_long_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_long_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_long_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_long(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_long_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_long_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_long_min(self.ptr)
    def minmax(self):
        r1 = c_long()
        r2 = c_long()
        libgsl.gsl_matrix_long_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_long_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_long_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_long_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_long_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_long_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_long_isneg(self.ptr)
    



class matrix_long_view(matrix_long):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_long_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_long))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_long_view_from_gsl(matrix_long):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_ulong(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_ulong)),
                ('block',  POINTER(gsl_block_ulong)),
                ('owner',  c_int)]
class gsl_matrix_ulong_view(Structure):
    _fields_ = [('matrix', gsl_matrix_ulong)]

_set_types('matrix_ulong_alloc', POINTER(gsl_matrix_ulong), [c_size_t, c_size_t])
_set_types('matrix_ulong_free', None, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_get', c_ulong, [POINTER(gsl_matrix_ulong), c_size_t, c_size_t])
_set_types('matrix_ulong_set', None, [POINTER(gsl_matrix_ulong), c_size_t, c_size_t, c_ulong])

_set_types('matrix_ulong_set_all',   None, [POINTER(gsl_matrix_ulong), c_ulong])
_set_types('matrix_ulong_set_zero',  None, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_set_identity', None, [POINTER(gsl_matrix_ulong)])

_set_types('matrix_ulong_submatrix', gsl_matrix_ulong_view,
           [POINTER(gsl_matrix_ulong),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_ulong_row', gsl_vector_ulong_view, [POINTER(gsl_matrix_ulong), c_size_t])
_set_types('matrix_ulong_column', gsl_vector_ulong_view, [POINTER(gsl_matrix_ulong), c_size_t])
_set_types('matrix_ulong_diagonal', gsl_vector_ulong_view, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_subdiagonal', gsl_vector_ulong_view, [POINTER(gsl_matrix_ulong), c_size_t])
_set_types('matrix_ulong_superdiagonal', gsl_vector_ulong_view, [POINTER(gsl_matrix_ulong), c_size_t])


_set_types('matrix_ulong_memcpy', _gsl_check_status, [POINTER(gsl_matrix_ulong),
                                                        POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_swap',   _gsl_check_status, [POINTER(gsl_matrix_ulong),
                                                        POINTER(gsl_matrix_ulong)])

_set_types('matrix_ulong_get_row', _gsl_check_status, [POINTER(gsl_vector_ulong),
                                                         POINTER(gsl_matrix_ulong), c_size_t])
_set_types('matrix_ulong_get_col', _gsl_check_status, [POINTER(gsl_vector_ulong),
                                                         POINTER(gsl_matrix_ulong), c_size_t])
_set_types('matrix_ulong_set_row', _gsl_check_status, [POINTER(gsl_matrix_ulong), c_size_t,
                                                         POINTER(gsl_vector_ulong)])
_set_types('matrix_ulong_set_col', _gsl_check_status, [POINTER(gsl_matrix_ulong), c_size_t,
                                                         POINTER(gsl_vector_ulong)])

_set_types('matrix_ulong_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_ulong), c_size_t, c_size_t])
_set_types('matrix_ulong_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_ulong), c_size_t, c_size_t])
_set_types('matrix_ulong_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_ulong), c_size_t, c_size_t])

_set_types('matrix_ulong_transpose', _gsl_check_status, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_ulong),
                                                                  POINTER(gsl_matrix_ulong)])






_set_types('matrix_ulong_max', c_ulong, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_min', c_ulong, [POINTER(gsl_matrix_ulong)])
_set_types('matrix_ulong_minmax', None, [POINTER(gsl_matrix_ulong),
                                           POINTER(c_ulong), POINTER(c_ulong)])
_set_types('matrix_ulong_max_index', None, [POINTER(gsl_matrix_ulong),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_ulong_min_index', None, [POINTER(gsl_matrix_ulong),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_ulong_minmax_index', None, [POINTER(gsl_matrix_ulong),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_ulong_isnull', _int_to_bool, [POINTER(gsl_matrix_ulong)])




class matrix_ulong(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_ulong_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_ulong):
                libgsl.gsl_matrix_ulong_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_ulong_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_ulong_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_ulong_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_ulong_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_ulong_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_ulong_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_ulong_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_ulong_row(self.ptr, i)
        return vector_ulong_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_ulong_column(self.ptr, j)
        return vector_ulong_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_ulong_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_ulong_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_ulong_superdiagonal(self.ptr, k)
        return vector_ulong_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_ulong_subdiagonal(self.ptr, k)
        return vector_ulong_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_ulong_superdiagonal(self.ptr, k)
        return vector_ulong_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_ulong(*self.shape)
        libgsl.gsl_matrix_ulong_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_ulong_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_ulong_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_ulong_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_ulong_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_ulong_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_ulong_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_ulong_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_ulong_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_ulong_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_ulong(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_ulong_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_ulong_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_ulong_min(self.ptr)
    def minmax(self):
        r1 = c_ulong()
        r2 = c_ulong()
        libgsl.gsl_matrix_ulong_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_ulong_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_ulong_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_ulong_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_ulong_isnull(self.ptr)
    



class matrix_ulong_view(matrix_ulong):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_ulong_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_ulong))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_ulong_view_from_gsl(matrix_ulong):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_short(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_short)),
                ('block',  POINTER(gsl_block_short)),
                ('owner',  c_int)]
class gsl_matrix_short_view(Structure):
    _fields_ = [('matrix', gsl_matrix_short)]

_set_types('matrix_short_alloc', POINTER(gsl_matrix_short), [c_size_t, c_size_t])
_set_types('matrix_short_free', None, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_get', c_short, [POINTER(gsl_matrix_short), c_size_t, c_size_t])
_set_types('matrix_short_set', None, [POINTER(gsl_matrix_short), c_size_t, c_size_t, c_short])

_set_types('matrix_short_set_all',   None, [POINTER(gsl_matrix_short), c_short])
_set_types('matrix_short_set_zero',  None, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_set_identity', None, [POINTER(gsl_matrix_short)])

_set_types('matrix_short_submatrix', gsl_matrix_short_view,
           [POINTER(gsl_matrix_short),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_short_row', gsl_vector_short_view, [POINTER(gsl_matrix_short), c_size_t])
_set_types('matrix_short_column', gsl_vector_short_view, [POINTER(gsl_matrix_short), c_size_t])
_set_types('matrix_short_diagonal', gsl_vector_short_view, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_subdiagonal', gsl_vector_short_view, [POINTER(gsl_matrix_short), c_size_t])
_set_types('matrix_short_superdiagonal', gsl_vector_short_view, [POINTER(gsl_matrix_short), c_size_t])


_set_types('matrix_short_memcpy', _gsl_check_status, [POINTER(gsl_matrix_short),
                                                        POINTER(gsl_matrix_short)])
_set_types('matrix_short_swap',   _gsl_check_status, [POINTER(gsl_matrix_short),
                                                        POINTER(gsl_matrix_short)])

_set_types('matrix_short_get_row', _gsl_check_status, [POINTER(gsl_vector_short),
                                                         POINTER(gsl_matrix_short), c_size_t])
_set_types('matrix_short_get_col', _gsl_check_status, [POINTER(gsl_vector_short),
                                                         POINTER(gsl_matrix_short), c_size_t])
_set_types('matrix_short_set_row', _gsl_check_status, [POINTER(gsl_matrix_short), c_size_t,
                                                         POINTER(gsl_vector_short)])
_set_types('matrix_short_set_col', _gsl_check_status, [POINTER(gsl_matrix_short), c_size_t,
                                                         POINTER(gsl_vector_short)])

_set_types('matrix_short_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_short), c_size_t, c_size_t])
_set_types('matrix_short_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_short), c_size_t, c_size_t])
_set_types('matrix_short_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_short), c_size_t, c_size_t])

_set_types('matrix_short_transpose', _gsl_check_status, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_short),
                                                                  POINTER(gsl_matrix_short)])






_set_types('matrix_short_max', c_short, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_min', c_short, [POINTER(gsl_matrix_short)])
_set_types('matrix_short_minmax', None, [POINTER(gsl_matrix_short),
                                           POINTER(c_short), POINTER(c_short)])
_set_types('matrix_short_max_index', None, [POINTER(gsl_matrix_short),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_short_min_index', None, [POINTER(gsl_matrix_short),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_short_minmax_index', None, [POINTER(gsl_matrix_short),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_short_isnull', _int_to_bool, [POINTER(gsl_matrix_short)])

#_set_types('matrix_short_ispos', _int_to_bool, [POINTER(gsl_matrix_short)])
#_set_types('matrix_short_isneg', _int_to_bool, [POINTER(gsl_matrix_short)])




class matrix_short(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_short_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_short):
                libgsl.gsl_matrix_short_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_short_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_short_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_short_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_short_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_short_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_short_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_short_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_short_row(self.ptr, i)
        return vector_short_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_short_column(self.ptr, j)
        return vector_short_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_short_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_short_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_short_superdiagonal(self.ptr, k)
        return vector_short_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_short_subdiagonal(self.ptr, k)
        return vector_short_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_short_superdiagonal(self.ptr, k)
        return vector_short_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_short(*self.shape)
        libgsl.gsl_matrix_short_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_short_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_short_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_short_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_short_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_short_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_short_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_short_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_short_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_short_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_short(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_short_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_short_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_short_min(self.ptr)
    def minmax(self):
        r1 = c_short()
        r2 = c_short()
        libgsl.gsl_matrix_short_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_short_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_short_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_short_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_short_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_short_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_short_isneg(self.ptr)
    



class matrix_short_view(matrix_short):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_short_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_short))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_short_view_from_gsl(matrix_short):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_ushort(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_ushort)),
                ('block',  POINTER(gsl_block_ushort)),
                ('owner',  c_int)]
class gsl_matrix_ushort_view(Structure):
    _fields_ = [('matrix', gsl_matrix_ushort)]

_set_types('matrix_ushort_alloc', POINTER(gsl_matrix_ushort), [c_size_t, c_size_t])
_set_types('matrix_ushort_free', None, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_get', c_ushort, [POINTER(gsl_matrix_ushort), c_size_t, c_size_t])
_set_types('matrix_ushort_set', None, [POINTER(gsl_matrix_ushort), c_size_t, c_size_t, c_ushort])

_set_types('matrix_ushort_set_all',   None, [POINTER(gsl_matrix_ushort), c_ushort])
_set_types('matrix_ushort_set_zero',  None, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_set_identity', None, [POINTER(gsl_matrix_ushort)])

_set_types('matrix_ushort_submatrix', gsl_matrix_ushort_view,
           [POINTER(gsl_matrix_ushort),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_ushort_row', gsl_vector_ushort_view, [POINTER(gsl_matrix_ushort), c_size_t])
_set_types('matrix_ushort_column', gsl_vector_ushort_view, [POINTER(gsl_matrix_ushort), c_size_t])
_set_types('matrix_ushort_diagonal', gsl_vector_ushort_view, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_subdiagonal', gsl_vector_ushort_view, [POINTER(gsl_matrix_ushort), c_size_t])
_set_types('matrix_ushort_superdiagonal', gsl_vector_ushort_view, [POINTER(gsl_matrix_ushort), c_size_t])


_set_types('matrix_ushort_memcpy', _gsl_check_status, [POINTER(gsl_matrix_ushort),
                                                        POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_swap',   _gsl_check_status, [POINTER(gsl_matrix_ushort),
                                                        POINTER(gsl_matrix_ushort)])

_set_types('matrix_ushort_get_row', _gsl_check_status, [POINTER(gsl_vector_ushort),
                                                         POINTER(gsl_matrix_ushort), c_size_t])
_set_types('matrix_ushort_get_col', _gsl_check_status, [POINTER(gsl_vector_ushort),
                                                         POINTER(gsl_matrix_ushort), c_size_t])
_set_types('matrix_ushort_set_row', _gsl_check_status, [POINTER(gsl_matrix_ushort), c_size_t,
                                                         POINTER(gsl_vector_ushort)])
_set_types('matrix_ushort_set_col', _gsl_check_status, [POINTER(gsl_matrix_ushort), c_size_t,
                                                         POINTER(gsl_vector_ushort)])

_set_types('matrix_ushort_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_ushort), c_size_t, c_size_t])
_set_types('matrix_ushort_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_ushort), c_size_t, c_size_t])
_set_types('matrix_ushort_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_ushort), c_size_t, c_size_t])

_set_types('matrix_ushort_transpose', _gsl_check_status, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_ushort),
                                                                  POINTER(gsl_matrix_ushort)])






_set_types('matrix_ushort_max', c_ushort, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_min', c_ushort, [POINTER(gsl_matrix_ushort)])
_set_types('matrix_ushort_minmax', None, [POINTER(gsl_matrix_ushort),
                                           POINTER(c_ushort), POINTER(c_ushort)])
_set_types('matrix_ushort_max_index', None, [POINTER(gsl_matrix_ushort),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_ushort_min_index', None, [POINTER(gsl_matrix_ushort),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_ushort_minmax_index', None, [POINTER(gsl_matrix_ushort),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_ushort_isnull', _int_to_bool, [POINTER(gsl_matrix_ushort)])




class matrix_ushort(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_ushort_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_ushort):
                libgsl.gsl_matrix_ushort_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_ushort_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_ushort_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_ushort_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_ushort_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_ushort_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_ushort_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_ushort_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_ushort_row(self.ptr, i)
        return vector_ushort_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_ushort_column(self.ptr, j)
        return vector_ushort_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_ushort_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_ushort_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_ushort_superdiagonal(self.ptr, k)
        return vector_ushort_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_ushort_subdiagonal(self.ptr, k)
        return vector_ushort_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_ushort_superdiagonal(self.ptr, k)
        return vector_ushort_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_ushort(*self.shape)
        libgsl.gsl_matrix_ushort_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_ushort_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_ushort_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_ushort_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_ushort_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_ushort_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_ushort_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_ushort_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_ushort_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_ushort_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_ushort(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_ushort_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_ushort_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_ushort_min(self.ptr)
    def minmax(self):
        r1 = c_ushort()
        r2 = c_ushort()
        libgsl.gsl_matrix_ushort_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_ushort_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_ushort_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_ushort_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_ushort_isnull(self.ptr)
    



class matrix_ushort_view(matrix_ushort):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_ushort_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_ushort))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_ushort_view_from_gsl(matrix_ushort):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_char(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_char)),
                ('block',  POINTER(gsl_block_char)),
                ('owner',  c_int)]
class gsl_matrix_char_view(Structure):
    _fields_ = [('matrix', gsl_matrix_char)]

_set_types('matrix_char_alloc', POINTER(gsl_matrix_char), [c_size_t, c_size_t])
_set_types('matrix_char_free', None, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_get', c_char, [POINTER(gsl_matrix_char), c_size_t, c_size_t])
_set_types('matrix_char_set', None, [POINTER(gsl_matrix_char), c_size_t, c_size_t, c_char])

_set_types('matrix_char_set_all',   None, [POINTER(gsl_matrix_char), c_char])
_set_types('matrix_char_set_zero',  None, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_set_identity', None, [POINTER(gsl_matrix_char)])

_set_types('matrix_char_submatrix', gsl_matrix_char_view,
           [POINTER(gsl_matrix_char),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_char_row', gsl_vector_char_view, [POINTER(gsl_matrix_char), c_size_t])
_set_types('matrix_char_column', gsl_vector_char_view, [POINTER(gsl_matrix_char), c_size_t])
_set_types('matrix_char_diagonal', gsl_vector_char_view, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_subdiagonal', gsl_vector_char_view, [POINTER(gsl_matrix_char), c_size_t])
_set_types('matrix_char_superdiagonal', gsl_vector_char_view, [POINTER(gsl_matrix_char), c_size_t])


_set_types('matrix_char_memcpy', _gsl_check_status, [POINTER(gsl_matrix_char),
                                                        POINTER(gsl_matrix_char)])
_set_types('matrix_char_swap',   _gsl_check_status, [POINTER(gsl_matrix_char),
                                                        POINTER(gsl_matrix_char)])

_set_types('matrix_char_get_row', _gsl_check_status, [POINTER(gsl_vector_char),
                                                         POINTER(gsl_matrix_char), c_size_t])
_set_types('matrix_char_get_col', _gsl_check_status, [POINTER(gsl_vector_char),
                                                         POINTER(gsl_matrix_char), c_size_t])
_set_types('matrix_char_set_row', _gsl_check_status, [POINTER(gsl_matrix_char), c_size_t,
                                                         POINTER(gsl_vector_char)])
_set_types('matrix_char_set_col', _gsl_check_status, [POINTER(gsl_matrix_char), c_size_t,
                                                         POINTER(gsl_vector_char)])

_set_types('matrix_char_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_char), c_size_t, c_size_t])
_set_types('matrix_char_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_char), c_size_t, c_size_t])
_set_types('matrix_char_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_char), c_size_t, c_size_t])

_set_types('matrix_char_transpose', _gsl_check_status, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_char),
                                                                  POINTER(gsl_matrix_char)])






_set_types('matrix_char_max', c_char, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_min', c_char, [POINTER(gsl_matrix_char)])
_set_types('matrix_char_minmax', None, [POINTER(gsl_matrix_char),
                                           POINTER(c_char), POINTER(c_char)])
_set_types('matrix_char_max_index', None, [POINTER(gsl_matrix_char),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_char_min_index', None, [POINTER(gsl_matrix_char),
                                              POINTER(c_size_t), POINTER(c_size_t)])
_set_types('matrix_char_minmax_index', None, [POINTER(gsl_matrix_char),
                                                 POINTER(c_size_t), POINTER(c_size_t),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('matrix_char_isnull', _int_to_bool, [POINTER(gsl_matrix_char)])

#_set_types('matrix_char_ispos', _int_to_bool, [POINTER(gsl_matrix_char)])
#_set_types('matrix_char_isneg', _int_to_bool, [POINTER(gsl_matrix_char)])




class matrix_char(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_char_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_char):
                libgsl.gsl_matrix_char_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_char_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_char_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_char_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_char_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_char_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_char_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_char_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_char_row(self.ptr, i)
        return vector_char_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_char_column(self.ptr, j)
        return vector_char_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_char_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_char_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_char_superdiagonal(self.ptr, k)
        return vector_char_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_char_subdiagonal(self.ptr, k)
        return vector_char_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_char_superdiagonal(self.ptr, k)
        return vector_char_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_char(*self.shape)
        libgsl.gsl_matrix_char_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_char_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_char_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_char_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_char_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_char_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_char_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_char_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_char_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_char_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_char(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_char_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    
    def max(self):
        return libgsl.gsl_matrix_char_max(self.ptr)
    def min(self):
        return libgsl.gsl_matrix_char_min(self.ptr)
    def minmax(self):
        r1 = c_char()
        r2 = c_char()
        libgsl.gsl_matrix_char_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_char_max_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def min_index(self):
        i = c_size_t()
        j = c_size_t()
        libgsl.gsl_matrix_char_min_index(self.ptr, byref(i), byref(j))
        return i.value, j.value
    def minmax_index(self):
        imin = c_size_t()
        jmin = c_size_t()
        imax = c_size_t()
        jmax = c_size_t()
        libgsl.gsl_matrix_char_minmax_index(self.ptr, byref(imin), byref(jmin),
                                               byref(imax), byref(jmax))
        return imin.value, jmin.value, imax.value, jmax.value
    

    def isnull(self):
        return libgsl.gsl_matrix_char_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_matrix_char_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_matrix_char_isneg(self.ptr)
    



class matrix_char_view(matrix_char):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_char_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_char))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_char_view_from_gsl(matrix_char):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_complex(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(gsl_complex)),
                ('block',  POINTER(gsl_block_complex)),
                ('owner',  c_int)]
class gsl_matrix_complex_view(Structure):
    _fields_ = [('matrix', gsl_matrix_complex)]

_set_types('matrix_complex_alloc', POINTER(gsl_matrix_complex), [c_size_t, c_size_t])
_set_types('matrix_complex_free', None, [POINTER(gsl_matrix_complex)])
_set_types('matrix_complex_get', gsl_complex, [POINTER(gsl_matrix_complex), c_size_t, c_size_t])
_set_types('matrix_complex_set', None, [POINTER(gsl_matrix_complex), c_size_t, c_size_t, gsl_complex])

_set_types('matrix_complex_set_all',   None, [POINTER(gsl_matrix_complex), gsl_complex])
_set_types('matrix_complex_set_zero',  None, [POINTER(gsl_matrix_complex)])
_set_types('matrix_complex_set_identity', None, [POINTER(gsl_matrix_complex)])

_set_types('matrix_complex_submatrix', gsl_matrix_complex_view,
           [POINTER(gsl_matrix_complex),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_complex_row', gsl_vector_complex_view, [POINTER(gsl_matrix_complex), c_size_t])
_set_types('matrix_complex_column', gsl_vector_complex_view, [POINTER(gsl_matrix_complex), c_size_t])
_set_types('matrix_complex_diagonal', gsl_vector_complex_view, [POINTER(gsl_matrix_complex)])
_set_types('matrix_complex_subdiagonal', gsl_vector_complex_view, [POINTER(gsl_matrix_complex), c_size_t])
_set_types('matrix_complex_superdiagonal', gsl_vector_complex_view, [POINTER(gsl_matrix_complex), c_size_t])


_set_types('matrix_complex_memcpy', _gsl_check_status, [POINTER(gsl_matrix_complex),
                                                        POINTER(gsl_matrix_complex)])
_set_types('matrix_complex_swap',   _gsl_check_status, [POINTER(gsl_matrix_complex),
                                                        POINTER(gsl_matrix_complex)])

_set_types('matrix_complex_get_row', _gsl_check_status, [POINTER(gsl_vector_complex),
                                                         POINTER(gsl_matrix_complex), c_size_t])
_set_types('matrix_complex_get_col', _gsl_check_status, [POINTER(gsl_vector_complex),
                                                         POINTER(gsl_matrix_complex), c_size_t])
_set_types('matrix_complex_set_row', _gsl_check_status, [POINTER(gsl_matrix_complex), c_size_t,
                                                         POINTER(gsl_vector_complex)])
_set_types('matrix_complex_set_col', _gsl_check_status, [POINTER(gsl_matrix_complex), c_size_t,
                                                         POINTER(gsl_vector_complex)])

_set_types('matrix_complex_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_complex), c_size_t, c_size_t])
_set_types('matrix_complex_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_complex), c_size_t, c_size_t])
_set_types('matrix_complex_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_complex), c_size_t, c_size_t])

_set_types('matrix_complex_transpose', _gsl_check_status, [POINTER(gsl_matrix_complex)])
_set_types('matrix_complex_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_complex),
                                                                  POINTER(gsl_matrix_complex)])







_set_types('matrix_complex_isnull', _int_to_bool, [POINTER(gsl_matrix_complex)])




class matrix_complex(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_complex_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_complex):
                libgsl.gsl_matrix_complex_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_complex_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_complex_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_complex_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_complex_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_complex_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_complex_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_complex_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_complex_row(self.ptr, i)
        return vector_complex_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_complex_column(self.ptr, j)
        return vector_complex_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_complex_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_complex_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_complex_superdiagonal(self.ptr, k)
        return vector_complex_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_complex_subdiagonal(self.ptr, k)
        return vector_complex_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_complex_superdiagonal(self.ptr, k)
        return vector_complex_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_complex(*self.shape)
        libgsl.gsl_matrix_complex_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_complex_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_complex_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_complex_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_complex_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_complex_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_complex_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_complex_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_complex_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_complex_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_complex(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_complex_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    

    def isnull(self):
        return libgsl.gsl_matrix_complex_isnull(self.ptr)
    



class matrix_complex_view(matrix_complex):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_complex_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_complex))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_complex_view_from_gsl(matrix_complex):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_complex_float(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(gsl_complex_float)),
                ('block',  POINTER(gsl_block_complex_float)),
                ('owner',  c_int)]
class gsl_matrix_complex_float_view(Structure):
    _fields_ = [('matrix', gsl_matrix_complex_float)]

_set_types('matrix_complex_float_alloc', POINTER(gsl_matrix_complex_float), [c_size_t, c_size_t])
_set_types('matrix_complex_float_free', None, [POINTER(gsl_matrix_complex_float)])
_set_types('matrix_complex_float_get', gsl_complex_float, [POINTER(gsl_matrix_complex_float), c_size_t, c_size_t])
_set_types('matrix_complex_float_set', None, [POINTER(gsl_matrix_complex_float), c_size_t, c_size_t, gsl_complex_float])

_set_types('matrix_complex_float_set_all',   None, [POINTER(gsl_matrix_complex_float), gsl_complex_float])
_set_types('matrix_complex_float_set_zero',  None, [POINTER(gsl_matrix_complex_float)])
_set_types('matrix_complex_float_set_identity', None, [POINTER(gsl_matrix_complex_float)])

_set_types('matrix_complex_float_submatrix', gsl_matrix_complex_float_view,
           [POINTER(gsl_matrix_complex_float),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_complex_float_row', gsl_vector_complex_float_view, [POINTER(gsl_matrix_complex_float), c_size_t])
_set_types('matrix_complex_float_column', gsl_vector_complex_float_view, [POINTER(gsl_matrix_complex_float), c_size_t])
_set_types('matrix_complex_float_diagonal', gsl_vector_complex_float_view, [POINTER(gsl_matrix_complex_float)])
_set_types('matrix_complex_float_subdiagonal', gsl_vector_complex_float_view, [POINTER(gsl_matrix_complex_float), c_size_t])
_set_types('matrix_complex_float_superdiagonal', gsl_vector_complex_float_view, [POINTER(gsl_matrix_complex_float), c_size_t])


_set_types('matrix_complex_float_memcpy', _gsl_check_status, [POINTER(gsl_matrix_complex_float),
                                                        POINTER(gsl_matrix_complex_float)])
_set_types('matrix_complex_float_swap',   _gsl_check_status, [POINTER(gsl_matrix_complex_float),
                                                        POINTER(gsl_matrix_complex_float)])

_set_types('matrix_complex_float_get_row', _gsl_check_status, [POINTER(gsl_vector_complex_float),
                                                         POINTER(gsl_matrix_complex_float), c_size_t])
_set_types('matrix_complex_float_get_col', _gsl_check_status, [POINTER(gsl_vector_complex_float),
                                                         POINTER(gsl_matrix_complex_float), c_size_t])
_set_types('matrix_complex_float_set_row', _gsl_check_status, [POINTER(gsl_matrix_complex_float), c_size_t,
                                                         POINTER(gsl_vector_complex_float)])
_set_types('matrix_complex_float_set_col', _gsl_check_status, [POINTER(gsl_matrix_complex_float), c_size_t,
                                                         POINTER(gsl_vector_complex_float)])

_set_types('matrix_complex_float_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_complex_float), c_size_t, c_size_t])
_set_types('matrix_complex_float_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_complex_float), c_size_t, c_size_t])
_set_types('matrix_complex_float_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_complex_float), c_size_t, c_size_t])

_set_types('matrix_complex_float_transpose', _gsl_check_status, [POINTER(gsl_matrix_complex_float)])
_set_types('matrix_complex_float_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_complex_float),
                                                                  POINTER(gsl_matrix_complex_float)])







_set_types('matrix_complex_float_isnull', _int_to_bool, [POINTER(gsl_matrix_complex_float)])




class matrix_complex_float(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_complex_float_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_complex_float):
                libgsl.gsl_matrix_complex_float_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_complex_float_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_complex_float_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_complex_float_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_complex_float_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_complex_float_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_complex_float_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_complex_float_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_complex_float_row(self.ptr, i)
        return vector_complex_float_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_complex_float_column(self.ptr, j)
        return vector_complex_float_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_complex_float_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_complex_float_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_complex_float_superdiagonal(self.ptr, k)
        return vector_complex_float_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_complex_float_subdiagonal(self.ptr, k)
        return vector_complex_float_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_complex_float_superdiagonal(self.ptr, k)
        return vector_complex_float_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_complex_float(*self.shape)
        libgsl.gsl_matrix_complex_float_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_complex_float_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_complex_float_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_complex_float_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_complex_float_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_complex_float_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_complex_float_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_complex_float_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_complex_float_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_complex_float_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_complex_float(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_complex_float_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    

    def isnull(self):
        return libgsl.gsl_matrix_complex_float_isnull(self.ptr)
    



class matrix_complex_float_view(matrix_complex_float):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_complex_float_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_complex_float))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_complex_float_view_from_gsl(matrix_complex_float):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_matrix_uchar(Structure):
    _fields_ = [('size1', c_size_t),
                ('size2', c_size_t),
                ('tda', c_size_t),
                ('data',   POINTER(c_ubyte)),
                ('block',  POINTER(gsl_block_uchar)),
                ('owner',  c_int)]
class gsl_matrix_uchar_view(Structure):
    _fields_ = [('matrix', gsl_matrix_uchar)]

_set_types('matrix_uchar_alloc', POINTER(gsl_matrix_uchar), [c_size_t, c_size_t])
_set_types('matrix_uchar_free', None, [POINTER(gsl_matrix_uchar)])
_set_types('matrix_uchar_get', c_ubyte, [POINTER(gsl_matrix_uchar), c_size_t, c_size_t])
_set_types('matrix_uchar_set', None, [POINTER(gsl_matrix_uchar), c_size_t, c_size_t, c_ubyte])

_set_types('matrix_uchar_set_all',   None, [POINTER(gsl_matrix_uchar), c_ubyte])
_set_types('matrix_uchar_set_zero',  None, [POINTER(gsl_matrix_uchar)])
_set_types('matrix_uchar_set_identity', None, [POINTER(gsl_matrix_uchar)])

_set_types('matrix_uchar_submatrix', gsl_matrix_uchar_view,
           [POINTER(gsl_matrix_uchar),
            c_size_t, c_size_t,
            c_size_t, c_size_t])
_set_types('matrix_uchar_row', gsl_vector_uchar_view, [POINTER(gsl_matrix_uchar), c_size_t])
_set_types('matrix_uchar_column', gsl_vector_uchar_view, [POINTER(gsl_matrix_uchar), c_size_t])
_set_types('matrix_uchar_diagonal', gsl_vector_uchar_view, [POINTER(gsl_matrix_uchar)])
_set_types('matrix_uchar_subdiagonal', gsl_vector_uchar_view, [POINTER(gsl_matrix_uchar), c_size_t])
_set_types('matrix_uchar_superdiagonal', gsl_vector_uchar_view, [POINTER(gsl_matrix_uchar), c_size_t])


_set_types('matrix_uchar_memcpy', _gsl_check_status, [POINTER(gsl_matrix_uchar),
                                                        POINTER(gsl_matrix_uchar)])
_set_types('matrix_uchar_swap',   _gsl_check_status, [POINTER(gsl_matrix_uchar),
                                                        POINTER(gsl_matrix_uchar)])

_set_types('matrix_uchar_get_row', _gsl_check_status, [POINTER(gsl_vector_uchar),
                                                         POINTER(gsl_matrix_uchar), c_size_t])
_set_types('matrix_uchar_get_col', _gsl_check_status, [POINTER(gsl_vector_uchar),
                                                         POINTER(gsl_matrix_uchar), c_size_t])
_set_types('matrix_uchar_set_row', _gsl_check_status, [POINTER(gsl_matrix_uchar), c_size_t,
                                                         POINTER(gsl_vector_uchar)])
_set_types('matrix_uchar_set_col', _gsl_check_status, [POINTER(gsl_matrix_uchar), c_size_t,
                                                         POINTER(gsl_vector_uchar)])

_set_types('matrix_uchar_swap_rows', _gsl_check_status, [POINTER(gsl_matrix_uchar), c_size_t, c_size_t])
_set_types('matrix_uchar_swap_columns', _gsl_check_status, [POINTER(gsl_matrix_uchar), c_size_t, c_size_t])
_set_types('matrix_uchar_swap_rowcol', _gsl_check_status, [POINTER(gsl_matrix_uchar), c_size_t, c_size_t])

_set_types('matrix_uchar_transpose', _gsl_check_status, [POINTER(gsl_matrix_uchar)])
_set_types('matrix_uchar_transpose_memcpy', _gsl_check_status, [POINTER(gsl_matrix_uchar),
                                                                  POINTER(gsl_matrix_uchar)])







_set_types('matrix_uchar_isnull', _int_to_bool, [POINTER(gsl_matrix_uchar)])




class matrix_uchar(matrix_base):
    def __init__(self, n1, n2 = None):
        self.libgsl = libgsl # help during __del__
        if hasattr(n1, 'shape'):
            initializer = n1
            n1, n2 = initializer.shape
        elif n2 is None:
            try:
                initializer = n1
                n1 = len(initializer)
                n2 = len(initializer[0])
            except:
                initializer = None
        else:
            initializer = None
        self.ptr = libgsl.gsl_matrix_uchar_alloc(n1, n2)
        _gsl_check_null_pointer(self.ptr)
        self.shape = (n1, n2)
        if initializer is not None:
            if isinstance(initializer, matrix_uchar):
                libgsl.gsl_matrix_uchar_memcpy(self.ptr, initializer.ptr)
            elif hasattr(initializer, 'shape'):
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[(i, j)]
            else:
                for j in xrange(n2):
                    for i in xrange(n1):
                        self[i, j] = initializer[i][j]
    def __del__(self):
        self.libgsl.gsl_matrix_uchar_free(self.ptr)
    def __getitem__(self, ij):
        return libgsl.gsl_matrix_uchar_get(self.ptr, ij[0], ij[1])
    def __setitem__(self, ij, x):
        return libgsl.gsl_matrix_uchar_set(self.ptr, ij[0], ij[1], x)

    def set_all(self, x = 0):
        libgsl.gsl_matrix_uchar_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_matrix_uchar_set_zero(self.ptr)
    def set_identity(self):
        libgsl.gsl_matrix_uchar_set_identity(self.ptr)

    def submatrix(self, k1, k2, n1, n2):
        return matrix_uchar_view(self, k1, k2, n1, n2)
    def row(self, i):
        view = libgsl.gsl_matrix_uchar_row(self.ptr, i)
        return vector_uchar_view(None, -1, -1, _view = view)
    def column(self, j):
        view = libgsl.gsl_matrix_uchar_column(self.ptr, j)
        return vector_uchar_view(None, -1, -1, _view = view)
    def diagonal(self, k = 0):
        if k == 0:
            view = libgsl.gsl_matrix_uchar_diagonal(self.ptr)
        elif k < 0:
            view = libgsl.gsl_matrix_uchar_subdiagonal(self.ptr, -k)
        else:
            view = libgsl.gsl_matrix_uchar_superdiagonal(self.ptr, k)
        return vector_uchar_view(None, -1, -1, _view = view)
    def subdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_uchar_subdiagonal(self.ptr, k)
        return vector_uchar_view(None, -1, -1, _view = view)
    def superdiagonal(self, k = 1):
        view = libgsl.gsl_matrix_uchar_superdiagonal(self.ptr, k)
        return vector_uchar_view(None, -1, -1, _view = view)

    def rowiter(self):
        def row_iterator(m):
            for i in xrange(m.shape[0]):
                yield m.row(i)
        return row_iterator(self)
    def columniter(self):
        def column_iterator(m):
            for j in xrange(m.shape[1]):
                yield m.column(j)
        return column_iterator(self)

    def copy(self):
        new_m = matrix_uchar(*self.shape)
        libgsl.gsl_matrix_uchar_memcpy(new_m.ptr, self.ptr)
        return new_m
    def swap(self, other):
        libgsl.gsl_matrix_uchar_swap(self.ptr, other.ptr)

    def copy_row(self, i, vec):
        libgsl.gsl_matrix_uchar_get_row(vec.ptr, self.ptr, i)
    def copy_col(self, i, vec):
        libgsl.gsl_matrix_uchar_get_col(vec.ptr, self.ptr, i)
    def set_row(self, i, vec):
        libgsl.gsl_matrix_uchar_set_row(self.ptr, i, vec.ptr)
    def set_col(self, i, vec):
        libgsl.gsl_matrix_uchar_set_col(self.ptr, i, vec.ptr)

    def swap_rows(self, i, j):
        libgsl.gsl_matrix_uchar_swap_rows(self.ptr, i, j)
    def swap_columns(self, i, j):
        libgsl.gsl_matrix_uchar_swap_columns(self.ptr, i, j)
    def swap_rowcol(self, i, j):
        libgsl.gsl_matrix_uchar_swap_rowcol(self.ptr, i, j)

    def transpose(self):
        """In place transpose.

        Requires a square matrix."""
        libgsl.gsl_matrix_uchar_transpose(self.ptr)
    def T(self):
        """Return a trnasposed copy."""
        new_m = matrix_uchar(self.shape[1], self.shape[0])
        libgsl.gsl_matrix_uchar_transpose_memcpy(new_m.ptr, self.ptr)
        return new_m

    

    

    def isnull(self):
        return libgsl.gsl_matrix_uchar_isnull(self.ptr)
    



class matrix_uchar_view(matrix_uchar):
    def __init__(self, matrix, k1, k2, n1, n2):
        self.ref = matrix # prevent deallocation of matrix until the
                          # view is there
        self.shape = (n1, n2)
        view = libgsl.gsl_matrix_uchar_submatrix(matrix.ptr, k1, k2, n1, n2)
        self.ptr = cast(pointer(view), POINTER(gsl_matrix_uchar))
    def __del__(self):
        # don't need to free any memory
        pass

class _matrix_uchar_view_from_gsl(matrix_uchar):
    def __init__(self, gsl_matrix_ptr):
        #print "w", type(gsl_matrix_ptr.contents.size1)
        self.shape = (gsl_matrix_ptr.contents.size1,
                      gsl_matrix_ptr.contents.size2)
        self.ptr = gsl_matrix_ptr
    def __del__(self):
        # don't need to free any memory
        pass


