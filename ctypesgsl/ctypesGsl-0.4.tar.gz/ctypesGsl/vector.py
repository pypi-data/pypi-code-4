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

from vector_base import *


class gsl_vector(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_double)),
                ('block',  POINTER(gsl_block)),
                ('owner',  c_int)]
class gsl_vector_view(Structure):
    _fields_ = [('vector', gsl_vector)]

_set_types('vector_alloc', POINTER(gsl_vector), [c_size_t])
_set_types('vector_free', None, [POINTER(gsl_vector)])
_set_types('vector_get', c_double, [POINTER(gsl_vector), c_size_t])
_set_types('vector_set', None, [POINTER(gsl_vector), c_size_t, c_double])

_set_types('vector_set_all',   None, [POINTER(gsl_vector), c_double])
_set_types('vector_set_zero',  None, [POINTER(gsl_vector)])
_set_types('vector_set_basis', _gsl_check_status, [POINTER(gsl_vector), c_size_t])

_set_types('vector_subvector', gsl_vector_view,
           [POINTER(gsl_vector), c_size_t, c_size_t])
_set_types('vector_subvector_with_stride', gsl_vector_view,
           [POINTER(gsl_vector), c_size_t, c_size_t, c_size_t])




_set_types('vector_memcpy', _gsl_check_status, [POINTER(gsl_vector),
                                                        POINTER(gsl_vector)])
_set_types('vector_swap',   _gsl_check_status, [POINTER(gsl_vector),
                                                        POINTER(gsl_vector)])

_set_types('vector_swap_elements', _gsl_check_status, [POINTER(gsl_vector),
                                                               c_size_t, c_size_t])
_set_types('vector_reverse', _gsl_check_status, [POINTER(gsl_vector)])


_set_types('vector_add', _gsl_check_status, [POINTER(gsl_vector),
                                                     POINTER(gsl_vector)])
_set_types('vector_sub', _gsl_check_status, [POINTER(gsl_vector),
                                                     POINTER(gsl_vector)])
_set_types('vector_mul', _gsl_check_status, [POINTER(gsl_vector),
                                                     POINTER(gsl_vector)])
_set_types('vector_div', _gsl_check_status, [POINTER(gsl_vector),
                                                     POINTER(gsl_vector)])


_set_types('vector_scale', _gsl_check_status, [POINTER(gsl_vector),
                                                       c_double])
_set_types('vector_add_constant', _gsl_check_status, [POINTER(gsl_vector),
                                                              c_double])



_set_types('vector_max', c_double, [POINTER(gsl_vector)])
_set_types('vector_min', c_double, [POINTER(gsl_vector)])
_set_types('vector_minmax', None, [POINTER(gsl_vector),
                                           POINTER(c_double), POINTER(c_double)])
_set_types('vector_max_index', c_size_t, [POINTER(gsl_vector)])
_set_types('vector_min_index', c_size_t, [POINTER(gsl_vector)])
_set_types('vector_minmax_index', None, [POINTER(gsl_vector),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_isnull', _int_to_bool, [POINTER(gsl_vector)])

#_set_types('vector_ispos', _int_to_bool, [POINTER(gsl_vector)])
#_set_types('vector_isneg', _int_to_bool, [POINTER(gsl_vector)])




class vector(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector(len(self))
        libgsl.gsl_vector_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_reverse(self.ptr)

    
    def __iadd__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_add_constant(self.ptr, other)
        else:
            libgsl.gsl_vector_add(self.ptr, other.ptr)
        return self
    def __isub__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_add_constant(self.ptr, -other)
        else:
            libgsl.gsl_vector_sub(self.ptr, other.ptr)
        return self
    def __imul__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_scale(self.ptr, other)
        else:
            libgsl.gsl_vector_mul(self.ptr, other.ptr)
        return self
    def __idiv__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_scale(self.ptr, 1.0 / other)
        else:
            libgsl.gsl_vector_div(self.ptr, other.ptr)
        return self
    

    
    def max(self):
        return libgsl.gsl_vector_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_min(self.ptr)
    def minmax(self):
        r1 = c_double()
        r2 = c_double()
        libgsl.gsl_vector_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_isneg(self.ptr)
    


class vector_view(vector):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_view_from_gsl(vector):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_float(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_float)),
                ('block',  POINTER(gsl_block_float)),
                ('owner',  c_int)]
class gsl_vector_float_view(Structure):
    _fields_ = [('vector', gsl_vector_float)]

_set_types('vector_float_alloc', POINTER(gsl_vector_float), [c_size_t])
_set_types('vector_float_free', None, [POINTER(gsl_vector_float)])
_set_types('vector_float_get', c_float, [POINTER(gsl_vector_float), c_size_t])
_set_types('vector_float_set', None, [POINTER(gsl_vector_float), c_size_t, c_float])

_set_types('vector_float_set_all',   None, [POINTER(gsl_vector_float), c_float])
_set_types('vector_float_set_zero',  None, [POINTER(gsl_vector_float)])
_set_types('vector_float_set_basis', _gsl_check_status, [POINTER(gsl_vector_float), c_size_t])

_set_types('vector_float_subvector', gsl_vector_float_view,
           [POINTER(gsl_vector_float), c_size_t, c_size_t])
_set_types('vector_float_subvector_with_stride', gsl_vector_float_view,
           [POINTER(gsl_vector_float), c_size_t, c_size_t, c_size_t])




_set_types('vector_float_memcpy', _gsl_check_status, [POINTER(gsl_vector_float),
                                                        POINTER(gsl_vector_float)])
_set_types('vector_float_swap',   _gsl_check_status, [POINTER(gsl_vector_float),
                                                        POINTER(gsl_vector_float)])

_set_types('vector_float_swap_elements', _gsl_check_status, [POINTER(gsl_vector_float),
                                                               c_size_t, c_size_t])
_set_types('vector_float_reverse', _gsl_check_status, [POINTER(gsl_vector_float)])


_set_types('vector_float_add', _gsl_check_status, [POINTER(gsl_vector_float),
                                                     POINTER(gsl_vector_float)])
_set_types('vector_float_sub', _gsl_check_status, [POINTER(gsl_vector_float),
                                                     POINTER(gsl_vector_float)])
_set_types('vector_float_mul', _gsl_check_status, [POINTER(gsl_vector_float),
                                                     POINTER(gsl_vector_float)])
_set_types('vector_float_div', _gsl_check_status, [POINTER(gsl_vector_float),
                                                     POINTER(gsl_vector_float)])


_set_types('vector_float_scale', _gsl_check_status, [POINTER(gsl_vector_float),
                                                       c_double])
_set_types('vector_float_add_constant', _gsl_check_status, [POINTER(gsl_vector_float),
                                                              c_double])



_set_types('vector_float_max', c_float, [POINTER(gsl_vector_float)])
_set_types('vector_float_min', c_float, [POINTER(gsl_vector_float)])
_set_types('vector_float_minmax', None, [POINTER(gsl_vector_float),
                                           POINTER(c_float), POINTER(c_float)])
_set_types('vector_float_max_index', c_size_t, [POINTER(gsl_vector_float)])
_set_types('vector_float_min_index', c_size_t, [POINTER(gsl_vector_float)])
_set_types('vector_float_minmax_index', None, [POINTER(gsl_vector_float),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_float_isnull', _int_to_bool, [POINTER(gsl_vector_float)])

#_set_types('vector_float_ispos', _int_to_bool, [POINTER(gsl_vector_float)])
#_set_types('vector_float_isneg', _int_to_bool, [POINTER(gsl_vector_float)])




class vector_float(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_float_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_float_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_float_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_float_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_float_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_float_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_float_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_float_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_float(len(self))
        libgsl.gsl_vector_float_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_float_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_float_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_float_reverse(self.ptr)

    
    def __iadd__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_float_add_constant(self.ptr, other)
        else:
            libgsl.gsl_vector_float_add(self.ptr, other.ptr)
        return self
    def __isub__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_float_add_constant(self.ptr, -other)
        else:
            libgsl.gsl_vector_float_sub(self.ptr, other.ptr)
        return self
    def __imul__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_float_scale(self.ptr, other)
        else:
            libgsl.gsl_vector_float_mul(self.ptr, other.ptr)
        return self
    def __idiv__(self, other):
        if isinstance(other, (float, int, long)):
            libgsl.gsl_vector_float_scale(self.ptr, 1.0 / other)
        else:
            libgsl.gsl_vector_float_div(self.ptr, other.ptr)
        return self
    

    
    def max(self):
        return libgsl.gsl_vector_float_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_float_min(self.ptr)
    def minmax(self):
        r1 = c_float()
        r2 = c_float()
        libgsl.gsl_vector_float_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_float_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_float_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_float_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_float_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_float_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_float_isneg(self.ptr)
    


class vector_float_view(vector_float):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_float_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_float_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_float))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_float_view_from_gsl(vector_float):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_int(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_int)),
                ('block',  POINTER(gsl_block_int)),
                ('owner',  c_int)]
class gsl_vector_int_view(Structure):
    _fields_ = [('vector', gsl_vector_int)]

_set_types('vector_int_alloc', POINTER(gsl_vector_int), [c_size_t])
_set_types('vector_int_free', None, [POINTER(gsl_vector_int)])
_set_types('vector_int_get', c_int, [POINTER(gsl_vector_int), c_size_t])
_set_types('vector_int_set', None, [POINTER(gsl_vector_int), c_size_t, c_int])

_set_types('vector_int_set_all',   None, [POINTER(gsl_vector_int), c_int])
_set_types('vector_int_set_zero',  None, [POINTER(gsl_vector_int)])
_set_types('vector_int_set_basis', _gsl_check_status, [POINTER(gsl_vector_int), c_size_t])

_set_types('vector_int_subvector', gsl_vector_int_view,
           [POINTER(gsl_vector_int), c_size_t, c_size_t])
_set_types('vector_int_subvector_with_stride', gsl_vector_int_view,
           [POINTER(gsl_vector_int), c_size_t, c_size_t, c_size_t])




_set_types('vector_int_memcpy', _gsl_check_status, [POINTER(gsl_vector_int),
                                                        POINTER(gsl_vector_int)])
_set_types('vector_int_swap',   _gsl_check_status, [POINTER(gsl_vector_int),
                                                        POINTER(gsl_vector_int)])

_set_types('vector_int_swap_elements', _gsl_check_status, [POINTER(gsl_vector_int),
                                                               c_size_t, c_size_t])
_set_types('vector_int_reverse', _gsl_check_status, [POINTER(gsl_vector_int)])





_set_types('vector_int_max', c_int, [POINTER(gsl_vector_int)])
_set_types('vector_int_min', c_int, [POINTER(gsl_vector_int)])
_set_types('vector_int_minmax', None, [POINTER(gsl_vector_int),
                                           POINTER(c_int), POINTER(c_int)])
_set_types('vector_int_max_index', c_size_t, [POINTER(gsl_vector_int)])
_set_types('vector_int_min_index', c_size_t, [POINTER(gsl_vector_int)])
_set_types('vector_int_minmax_index', None, [POINTER(gsl_vector_int),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_int_isnull', _int_to_bool, [POINTER(gsl_vector_int)])

#_set_types('vector_int_ispos', _int_to_bool, [POINTER(gsl_vector_int)])
#_set_types('vector_int_isneg', _int_to_bool, [POINTER(gsl_vector_int)])




class vector_int(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_int_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_int_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_int_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_int_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_int_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_int_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_int_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_int_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_int(len(self))
        libgsl.gsl_vector_int_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_int_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_int_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_int_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_int_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_int_min(self.ptr)
    def minmax(self):
        r1 = c_int()
        r2 = c_int()
        libgsl.gsl_vector_int_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_int_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_int_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_int_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_int_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_int_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_int_isneg(self.ptr)
    


class vector_int_view(vector_int):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_int_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_int_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_int))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_int_view_from_gsl(vector_int):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_uint(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_uint)),
                ('block',  POINTER(gsl_block_uint)),
                ('owner',  c_int)]
class gsl_vector_uint_view(Structure):
    _fields_ = [('vector', gsl_vector_uint)]

_set_types('vector_uint_alloc', POINTER(gsl_vector_uint), [c_size_t])
_set_types('vector_uint_free', None, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_get', c_uint, [POINTER(gsl_vector_uint), c_size_t])
_set_types('vector_uint_set', None, [POINTER(gsl_vector_uint), c_size_t, c_uint])

_set_types('vector_uint_set_all',   None, [POINTER(gsl_vector_uint), c_uint])
_set_types('vector_uint_set_zero',  None, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_set_basis', _gsl_check_status, [POINTER(gsl_vector_uint), c_size_t])

_set_types('vector_uint_subvector', gsl_vector_uint_view,
           [POINTER(gsl_vector_uint), c_size_t, c_size_t])
_set_types('vector_uint_subvector_with_stride', gsl_vector_uint_view,
           [POINTER(gsl_vector_uint), c_size_t, c_size_t, c_size_t])




_set_types('vector_uint_memcpy', _gsl_check_status, [POINTER(gsl_vector_uint),
                                                        POINTER(gsl_vector_uint)])
_set_types('vector_uint_swap',   _gsl_check_status, [POINTER(gsl_vector_uint),
                                                        POINTER(gsl_vector_uint)])

_set_types('vector_uint_swap_elements', _gsl_check_status, [POINTER(gsl_vector_uint),
                                                               c_size_t, c_size_t])
_set_types('vector_uint_reverse', _gsl_check_status, [POINTER(gsl_vector_uint)])





_set_types('vector_uint_max', c_uint, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_min', c_uint, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_minmax', None, [POINTER(gsl_vector_uint),
                                           POINTER(c_uint), POINTER(c_uint)])
_set_types('vector_uint_max_index', c_size_t, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_min_index', c_size_t, [POINTER(gsl_vector_uint)])
_set_types('vector_uint_minmax_index', None, [POINTER(gsl_vector_uint),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_uint_isnull', _int_to_bool, [POINTER(gsl_vector_uint)])




class vector_uint(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_uint_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_uint_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_uint_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_uint_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_uint_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_uint_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_uint_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_uint_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_uint(len(self))
        libgsl.gsl_vector_uint_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_uint_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_uint_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_uint_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_uint_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_uint_min(self.ptr)
    def minmax(self):
        r1 = c_uint()
        r2 = c_uint()
        libgsl.gsl_vector_uint_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_uint_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_uint_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_uint_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_uint_isnull(self.ptr)
    


class vector_uint_view(vector_uint):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_uint_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_uint_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_uint))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_uint_view_from_gsl(vector_uint):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_long(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_long)),
                ('block',  POINTER(gsl_block_long)),
                ('owner',  c_int)]
class gsl_vector_long_view(Structure):
    _fields_ = [('vector', gsl_vector_long)]

_set_types('vector_long_alloc', POINTER(gsl_vector_long), [c_size_t])
_set_types('vector_long_free', None, [POINTER(gsl_vector_long)])
_set_types('vector_long_get', c_long, [POINTER(gsl_vector_long), c_size_t])
_set_types('vector_long_set', None, [POINTER(gsl_vector_long), c_size_t, c_long])

_set_types('vector_long_set_all',   None, [POINTER(gsl_vector_long), c_long])
_set_types('vector_long_set_zero',  None, [POINTER(gsl_vector_long)])
_set_types('vector_long_set_basis', _gsl_check_status, [POINTER(gsl_vector_long), c_size_t])

_set_types('vector_long_subvector', gsl_vector_long_view,
           [POINTER(gsl_vector_long), c_size_t, c_size_t])
_set_types('vector_long_subvector_with_stride', gsl_vector_long_view,
           [POINTER(gsl_vector_long), c_size_t, c_size_t, c_size_t])




_set_types('vector_long_memcpy', _gsl_check_status, [POINTER(gsl_vector_long),
                                                        POINTER(gsl_vector_long)])
_set_types('vector_long_swap',   _gsl_check_status, [POINTER(gsl_vector_long),
                                                        POINTER(gsl_vector_long)])

_set_types('vector_long_swap_elements', _gsl_check_status, [POINTER(gsl_vector_long),
                                                               c_size_t, c_size_t])
_set_types('vector_long_reverse', _gsl_check_status, [POINTER(gsl_vector_long)])





_set_types('vector_long_max', c_long, [POINTER(gsl_vector_long)])
_set_types('vector_long_min', c_long, [POINTER(gsl_vector_long)])
_set_types('vector_long_minmax', None, [POINTER(gsl_vector_long),
                                           POINTER(c_long), POINTER(c_long)])
_set_types('vector_long_max_index', c_size_t, [POINTER(gsl_vector_long)])
_set_types('vector_long_min_index', c_size_t, [POINTER(gsl_vector_long)])
_set_types('vector_long_minmax_index', None, [POINTER(gsl_vector_long),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_long_isnull', _int_to_bool, [POINTER(gsl_vector_long)])

#_set_types('vector_long_ispos', _int_to_bool, [POINTER(gsl_vector_long)])
#_set_types('vector_long_isneg', _int_to_bool, [POINTER(gsl_vector_long)])




class vector_long(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_long_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_long_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_long_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_long_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_long_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_long_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_long_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_long_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_long(len(self))
        libgsl.gsl_vector_long_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_long_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_long_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_long_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_long_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_long_min(self.ptr)
    def minmax(self):
        r1 = c_long()
        r2 = c_long()
        libgsl.gsl_vector_long_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_long_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_long_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_long_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_long_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_long_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_long_isneg(self.ptr)
    


class vector_long_view(vector_long):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_long_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_long_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_long))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_long_view_from_gsl(vector_long):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_ulong(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_ulong)),
                ('block',  POINTER(gsl_block_ulong)),
                ('owner',  c_int)]
class gsl_vector_ulong_view(Structure):
    _fields_ = [('vector', gsl_vector_ulong)]

_set_types('vector_ulong_alloc', POINTER(gsl_vector_ulong), [c_size_t])
_set_types('vector_ulong_free', None, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_get', c_ulong, [POINTER(gsl_vector_ulong), c_size_t])
_set_types('vector_ulong_set', None, [POINTER(gsl_vector_ulong), c_size_t, c_ulong])

_set_types('vector_ulong_set_all',   None, [POINTER(gsl_vector_ulong), c_ulong])
_set_types('vector_ulong_set_zero',  None, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_set_basis', _gsl_check_status, [POINTER(gsl_vector_ulong), c_size_t])

_set_types('vector_ulong_subvector', gsl_vector_ulong_view,
           [POINTER(gsl_vector_ulong), c_size_t, c_size_t])
_set_types('vector_ulong_subvector_with_stride', gsl_vector_ulong_view,
           [POINTER(gsl_vector_ulong), c_size_t, c_size_t, c_size_t])




_set_types('vector_ulong_memcpy', _gsl_check_status, [POINTER(gsl_vector_ulong),
                                                        POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_swap',   _gsl_check_status, [POINTER(gsl_vector_ulong),
                                                        POINTER(gsl_vector_ulong)])

_set_types('vector_ulong_swap_elements', _gsl_check_status, [POINTER(gsl_vector_ulong),
                                                               c_size_t, c_size_t])
_set_types('vector_ulong_reverse', _gsl_check_status, [POINTER(gsl_vector_ulong)])





_set_types('vector_ulong_max', c_ulong, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_min', c_ulong, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_minmax', None, [POINTER(gsl_vector_ulong),
                                           POINTER(c_ulong), POINTER(c_ulong)])
_set_types('vector_ulong_max_index', c_size_t, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_min_index', c_size_t, [POINTER(gsl_vector_ulong)])
_set_types('vector_ulong_minmax_index', None, [POINTER(gsl_vector_ulong),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_ulong_isnull', _int_to_bool, [POINTER(gsl_vector_ulong)])




class vector_ulong(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_ulong_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_ulong_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_ulong_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_ulong_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_ulong_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_ulong_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_ulong_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_ulong_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_ulong(len(self))
        libgsl.gsl_vector_ulong_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_ulong_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_ulong_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_ulong_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_ulong_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_ulong_min(self.ptr)
    def minmax(self):
        r1 = c_ulong()
        r2 = c_ulong()
        libgsl.gsl_vector_ulong_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_ulong_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_ulong_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_ulong_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_ulong_isnull(self.ptr)
    


class vector_ulong_view(vector_ulong):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_ulong_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_ulong_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_ulong))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_ulong_view_from_gsl(vector_ulong):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_short(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_short)),
                ('block',  POINTER(gsl_block_short)),
                ('owner',  c_int)]
class gsl_vector_short_view(Structure):
    _fields_ = [('vector', gsl_vector_short)]

_set_types('vector_short_alloc', POINTER(gsl_vector_short), [c_size_t])
_set_types('vector_short_free', None, [POINTER(gsl_vector_short)])
_set_types('vector_short_get', c_short, [POINTER(gsl_vector_short), c_size_t])
_set_types('vector_short_set', None, [POINTER(gsl_vector_short), c_size_t, c_short])

_set_types('vector_short_set_all',   None, [POINTER(gsl_vector_short), c_short])
_set_types('vector_short_set_zero',  None, [POINTER(gsl_vector_short)])
_set_types('vector_short_set_basis', _gsl_check_status, [POINTER(gsl_vector_short), c_size_t])

_set_types('vector_short_subvector', gsl_vector_short_view,
           [POINTER(gsl_vector_short), c_size_t, c_size_t])
_set_types('vector_short_subvector_with_stride', gsl_vector_short_view,
           [POINTER(gsl_vector_short), c_size_t, c_size_t, c_size_t])




_set_types('vector_short_memcpy', _gsl_check_status, [POINTER(gsl_vector_short),
                                                        POINTER(gsl_vector_short)])
_set_types('vector_short_swap',   _gsl_check_status, [POINTER(gsl_vector_short),
                                                        POINTER(gsl_vector_short)])

_set_types('vector_short_swap_elements', _gsl_check_status, [POINTER(gsl_vector_short),
                                                               c_size_t, c_size_t])
_set_types('vector_short_reverse', _gsl_check_status, [POINTER(gsl_vector_short)])





_set_types('vector_short_max', c_short, [POINTER(gsl_vector_short)])
_set_types('vector_short_min', c_short, [POINTER(gsl_vector_short)])
_set_types('vector_short_minmax', None, [POINTER(gsl_vector_short),
                                           POINTER(c_short), POINTER(c_short)])
_set_types('vector_short_max_index', c_size_t, [POINTER(gsl_vector_short)])
_set_types('vector_short_min_index', c_size_t, [POINTER(gsl_vector_short)])
_set_types('vector_short_minmax_index', None, [POINTER(gsl_vector_short),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_short_isnull', _int_to_bool, [POINTER(gsl_vector_short)])

#_set_types('vector_short_ispos', _int_to_bool, [POINTER(gsl_vector_short)])
#_set_types('vector_short_isneg', _int_to_bool, [POINTER(gsl_vector_short)])




class vector_short(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_short_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_short_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_short_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_short_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_short_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_short_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_short_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_short_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_short(len(self))
        libgsl.gsl_vector_short_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_short_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_short_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_short_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_short_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_short_min(self.ptr)
    def minmax(self):
        r1 = c_short()
        r2 = c_short()
        libgsl.gsl_vector_short_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_short_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_short_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_short_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_short_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_short_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_short_isneg(self.ptr)
    


class vector_short_view(vector_short):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_short_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_short_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_short))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_short_view_from_gsl(vector_short):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_ushort(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_ushort)),
                ('block',  POINTER(gsl_block_ushort)),
                ('owner',  c_int)]
class gsl_vector_ushort_view(Structure):
    _fields_ = [('vector', gsl_vector_ushort)]

_set_types('vector_ushort_alloc', POINTER(gsl_vector_ushort), [c_size_t])
_set_types('vector_ushort_free', None, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_get', c_ushort, [POINTER(gsl_vector_ushort), c_size_t])
_set_types('vector_ushort_set', None, [POINTER(gsl_vector_ushort), c_size_t, c_ushort])

_set_types('vector_ushort_set_all',   None, [POINTER(gsl_vector_ushort), c_ushort])
_set_types('vector_ushort_set_zero',  None, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_set_basis', _gsl_check_status, [POINTER(gsl_vector_ushort), c_size_t])

_set_types('vector_ushort_subvector', gsl_vector_ushort_view,
           [POINTER(gsl_vector_ushort), c_size_t, c_size_t])
_set_types('vector_ushort_subvector_with_stride', gsl_vector_ushort_view,
           [POINTER(gsl_vector_ushort), c_size_t, c_size_t, c_size_t])




_set_types('vector_ushort_memcpy', _gsl_check_status, [POINTER(gsl_vector_ushort),
                                                        POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_swap',   _gsl_check_status, [POINTER(gsl_vector_ushort),
                                                        POINTER(gsl_vector_ushort)])

_set_types('vector_ushort_swap_elements', _gsl_check_status, [POINTER(gsl_vector_ushort),
                                                               c_size_t, c_size_t])
_set_types('vector_ushort_reverse', _gsl_check_status, [POINTER(gsl_vector_ushort)])





_set_types('vector_ushort_max', c_ushort, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_min', c_ushort, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_minmax', None, [POINTER(gsl_vector_ushort),
                                           POINTER(c_ushort), POINTER(c_ushort)])
_set_types('vector_ushort_max_index', c_size_t, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_min_index', c_size_t, [POINTER(gsl_vector_ushort)])
_set_types('vector_ushort_minmax_index', None, [POINTER(gsl_vector_ushort),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_ushort_isnull', _int_to_bool, [POINTER(gsl_vector_ushort)])




class vector_ushort(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_ushort_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_ushort_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_ushort_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_ushort_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_ushort_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_ushort_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_ushort_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_ushort_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_ushort(len(self))
        libgsl.gsl_vector_ushort_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_ushort_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_ushort_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_ushort_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_ushort_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_ushort_min(self.ptr)
    def minmax(self):
        r1 = c_ushort()
        r2 = c_ushort()
        libgsl.gsl_vector_ushort_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_ushort_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_ushort_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_ushort_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_ushort_isnull(self.ptr)
    


class vector_ushort_view(vector_ushort):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_ushort_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_ushort_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_ushort))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_ushort_view_from_gsl(vector_ushort):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_char(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_char)),
                ('block',  POINTER(gsl_block_char)),
                ('owner',  c_int)]
class gsl_vector_char_view(Structure):
    _fields_ = [('vector', gsl_vector_char)]

_set_types('vector_char_alloc', POINTER(gsl_vector_char), [c_size_t])
_set_types('vector_char_free', None, [POINTER(gsl_vector_char)])
_set_types('vector_char_get', c_char, [POINTER(gsl_vector_char), c_size_t])
_set_types('vector_char_set', None, [POINTER(gsl_vector_char), c_size_t, c_char])

_set_types('vector_char_set_all',   None, [POINTER(gsl_vector_char), c_char])
_set_types('vector_char_set_zero',  None, [POINTER(gsl_vector_char)])
_set_types('vector_char_set_basis', _gsl_check_status, [POINTER(gsl_vector_char), c_size_t])

_set_types('vector_char_subvector', gsl_vector_char_view,
           [POINTER(gsl_vector_char), c_size_t, c_size_t])
_set_types('vector_char_subvector_with_stride', gsl_vector_char_view,
           [POINTER(gsl_vector_char), c_size_t, c_size_t, c_size_t])




_set_types('vector_char_memcpy', _gsl_check_status, [POINTER(gsl_vector_char),
                                                        POINTER(gsl_vector_char)])
_set_types('vector_char_swap',   _gsl_check_status, [POINTER(gsl_vector_char),
                                                        POINTER(gsl_vector_char)])

_set_types('vector_char_swap_elements', _gsl_check_status, [POINTER(gsl_vector_char),
                                                               c_size_t, c_size_t])
_set_types('vector_char_reverse', _gsl_check_status, [POINTER(gsl_vector_char)])





_set_types('vector_char_max', c_char, [POINTER(gsl_vector_char)])
_set_types('vector_char_min', c_char, [POINTER(gsl_vector_char)])
_set_types('vector_char_minmax', None, [POINTER(gsl_vector_char),
                                           POINTER(c_char), POINTER(c_char)])
_set_types('vector_char_max_index', c_size_t, [POINTER(gsl_vector_char)])
_set_types('vector_char_min_index', c_size_t, [POINTER(gsl_vector_char)])
_set_types('vector_char_minmax_index', None, [POINTER(gsl_vector_char),
                                                 POINTER(c_size_t), POINTER(c_size_t)])


_set_types('vector_char_isnull', _int_to_bool, [POINTER(gsl_vector_char)])

#_set_types('vector_char_ispos', _int_to_bool, [POINTER(gsl_vector_char)])
#_set_types('vector_char_isneg', _int_to_bool, [POINTER(gsl_vector_char)])




class vector_char(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_char_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_char_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_char_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_char_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_char_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_char_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_char_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_char_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_char(len(self))
        libgsl.gsl_vector_char_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_char_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_char_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_char_reverse(self.ptr)

    

    
    def max(self):
        return libgsl.gsl_vector_char_max(self.ptr)
    def min(self):
        return libgsl.gsl_vector_char_min(self.ptr)
    def minmax(self):
        r1 = c_char()
        r2 = c_char()
        libgsl.gsl_vector_char_minmax(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    def max_index(self):
        return libgsl.gsl_vector_char_max_index(self.ptr)
    def min_index(self):
        return libgsl.gsl_vector_char_min_index(self.ptr)
    def minmax_index(self):
        r1 = c_size_t()
        r2 = c_size_t()
        libgsl.gsl_vector_char_minmax_index(self.ptr, byref(r1), byref(r2))
        return r1.value, r2.value
    

    def isnull(self):
        return libgsl.gsl_vector_char_isnull(self.ptr)
    
    #def ispos(self):
    #    return libgsl.gsl_vector_char_ispos(self.ptr)
    #def isneg(self):
    #    return libgsl.gsl_vector_char_isneg(self.ptr)
    


class vector_char_view(vector_char):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_char_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_char_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_char))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_char_view_from_gsl(vector_char):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_complex(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(gsl_complex)),
                ('block',  POINTER(gsl_block_complex)),
                ('owner',  c_int)]
class gsl_vector_complex_view(Structure):
    _fields_ = [('vector', gsl_vector_complex)]

_set_types('vector_complex_alloc', POINTER(gsl_vector_complex), [c_size_t])
_set_types('vector_complex_free', None, [POINTER(gsl_vector_complex)])
_set_types('vector_complex_get', gsl_complex, [POINTER(gsl_vector_complex), c_size_t])
_set_types('vector_complex_set', None, [POINTER(gsl_vector_complex), c_size_t, gsl_complex])

_set_types('vector_complex_set_all',   None, [POINTER(gsl_vector_complex), gsl_complex])
_set_types('vector_complex_set_zero',  None, [POINTER(gsl_vector_complex)])
_set_types('vector_complex_set_basis', _gsl_check_status, [POINTER(gsl_vector_complex), c_size_t])

_set_types('vector_complex_subvector', gsl_vector_complex_view,
           [POINTER(gsl_vector_complex), c_size_t, c_size_t])
_set_types('vector_complex_subvector_with_stride', gsl_vector_complex_view,
           [POINTER(gsl_vector_complex), c_size_t, c_size_t, c_size_t])


_set_types('vector_complex_real', gsl_vector_view,
           [POINTER(gsl_vector_complex)])
_set_types('vector_complex_imag', gsl_vector_view,
           [POINTER(gsl_vector_complex)])



_set_types('vector_complex_memcpy', _gsl_check_status, [POINTER(gsl_vector_complex),
                                                        POINTER(gsl_vector_complex)])
_set_types('vector_complex_swap',   _gsl_check_status, [POINTER(gsl_vector_complex),
                                                        POINTER(gsl_vector_complex)])

_set_types('vector_complex_swap_elements', _gsl_check_status, [POINTER(gsl_vector_complex),
                                                               c_size_t, c_size_t])
_set_types('vector_complex_reverse', _gsl_check_status, [POINTER(gsl_vector_complex)])






_set_types('vector_complex_isnull', _int_to_bool, [POINTER(gsl_vector_complex)])




class vector_complex(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_complex_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_complex_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_complex_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_complex_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_complex_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_complex_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_complex_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_complex_view(self, offset, n, stride)

    
    def real(self):
        v = libgsl.gsl_vector_complex_real(self.ptr)
        return vector_view(self, -1, -1, _view = v)
    def imag(self):
        v = libgsl.gsl_vector_complex_imag(self.ptr)
        return vector_view(self, -1, -1, _view = v)
    
    

    def copy(self):
        new_v = vector_complex(len(self))
        libgsl.gsl_vector_complex_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_complex_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_complex_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_complex_reverse(self.ptr)

    

    

    def isnull(self):
        return libgsl.gsl_vector_complex_isnull(self.ptr)
    


class vector_complex_view(vector_complex):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_complex_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_complex_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_complex))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_complex_view_from_gsl(vector_complex):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_complex_float(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(gsl_complex_float)),
                ('block',  POINTER(gsl_block_complex_float)),
                ('owner',  c_int)]
class gsl_vector_complex_float_view(Structure):
    _fields_ = [('vector', gsl_vector_complex_float)]

_set_types('vector_complex_float_alloc', POINTER(gsl_vector_complex_float), [c_size_t])
_set_types('vector_complex_float_free', None, [POINTER(gsl_vector_complex_float)])
_set_types('vector_complex_float_get', gsl_complex_float, [POINTER(gsl_vector_complex_float), c_size_t])
_set_types('vector_complex_float_set', None, [POINTER(gsl_vector_complex_float), c_size_t, gsl_complex_float])

_set_types('vector_complex_float_set_all',   None, [POINTER(gsl_vector_complex_float), gsl_complex_float])
_set_types('vector_complex_float_set_zero',  None, [POINTER(gsl_vector_complex_float)])
_set_types('vector_complex_float_set_basis', _gsl_check_status, [POINTER(gsl_vector_complex_float), c_size_t])

_set_types('vector_complex_float_subvector', gsl_vector_complex_float_view,
           [POINTER(gsl_vector_complex_float), c_size_t, c_size_t])
_set_types('vector_complex_float_subvector_with_stride', gsl_vector_complex_float_view,
           [POINTER(gsl_vector_complex_float), c_size_t, c_size_t, c_size_t])



_set_types('vector_complex_float_real', gsl_vector_float_view,
           [POINTER(gsl_vector_complex_float)])
_set_types('vector_complex_float_imag', gsl_vector_float_view,
           [POINTER(gsl_vector_complex_float)])


_set_types('vector_complex_float_memcpy', _gsl_check_status, [POINTER(gsl_vector_complex_float),
                                                        POINTER(gsl_vector_complex_float)])
_set_types('vector_complex_float_swap',   _gsl_check_status, [POINTER(gsl_vector_complex_float),
                                                        POINTER(gsl_vector_complex_float)])

_set_types('vector_complex_float_swap_elements', _gsl_check_status, [POINTER(gsl_vector_complex_float),
                                                               c_size_t, c_size_t])
_set_types('vector_complex_float_reverse', _gsl_check_status, [POINTER(gsl_vector_complex_float)])






_set_types('vector_complex_float_isnull', _int_to_bool, [POINTER(gsl_vector_complex_float)])




class vector_complex_float(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_complex_float_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_complex_float_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_complex_float_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_complex_float_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_complex_float_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_complex_float_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_complex_float_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_complex_float_view(self, offset, n, stride)

    
    
    def real(self):
        v = libgsl.gsl_vector_complex_float_real(self.ptr)
        return vector_float_view(self, -1, -1, _view = v)
    def imag(self):
        v = libgsl.gsl_vector_complex_float_imag(self.ptr)
        return vector_float_view(self, -1, -1, _view = v)
    

    def copy(self):
        new_v = vector_complex_float(len(self))
        libgsl.gsl_vector_complex_float_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_complex_float_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_complex_float_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_complex_float_reverse(self.ptr)

    

    

    def isnull(self):
        return libgsl.gsl_vector_complex_float_isnull(self.ptr)
    


class vector_complex_float_view(vector_complex_float):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_complex_float_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_complex_float_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_complex_float))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_complex_float_view_from_gsl(vector_complex_float):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass



class gsl_vector_uchar(Structure):
    _fields_ = [('size', c_size_t),
                ('stride', c_size_t),
                ('data',   POINTER(c_ubyte)),
                ('block',  POINTER(gsl_block_uchar)),
                ('owner',  c_int)]
class gsl_vector_uchar_view(Structure):
    _fields_ = [('vector', gsl_vector_uchar)]

_set_types('vector_uchar_alloc', POINTER(gsl_vector_uchar), [c_size_t])
_set_types('vector_uchar_free', None, [POINTER(gsl_vector_uchar)])
_set_types('vector_uchar_get', c_ubyte, [POINTER(gsl_vector_uchar), c_size_t])
_set_types('vector_uchar_set', None, [POINTER(gsl_vector_uchar), c_size_t, c_ubyte])

_set_types('vector_uchar_set_all',   None, [POINTER(gsl_vector_uchar), c_ubyte])
_set_types('vector_uchar_set_zero',  None, [POINTER(gsl_vector_uchar)])
_set_types('vector_uchar_set_basis', _gsl_check_status, [POINTER(gsl_vector_uchar), c_size_t])

_set_types('vector_uchar_subvector', gsl_vector_uchar_view,
           [POINTER(gsl_vector_uchar), c_size_t, c_size_t])
_set_types('vector_uchar_subvector_with_stride', gsl_vector_uchar_view,
           [POINTER(gsl_vector_uchar), c_size_t, c_size_t, c_size_t])




_set_types('vector_uchar_memcpy', _gsl_check_status, [POINTER(gsl_vector_uchar),
                                                        POINTER(gsl_vector_uchar)])
_set_types('vector_uchar_swap',   _gsl_check_status, [POINTER(gsl_vector_uchar),
                                                        POINTER(gsl_vector_uchar)])

_set_types('vector_uchar_swap_elements', _gsl_check_status, [POINTER(gsl_vector_uchar),
                                                               c_size_t, c_size_t])
_set_types('vector_uchar_reverse', _gsl_check_status, [POINTER(gsl_vector_uchar)])






_set_types('vector_uchar_isnull', _int_to_bool, [POINTER(gsl_vector_uchar)])




class vector_uchar(vector_base):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            n = initializer
            vect_init = False
        else:
            n = len(initializer)
            vect_init = True
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_vector_uchar_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if vect_init:
            for i, x in enumerate(initializer):
                self[i] = x
    def __del__(self):
        self.libgsl.gsl_vector_uchar_free(self.ptr)
    def __getitem__(self, i):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_uchar_get(self.ptr, i)
    def __setitem__(self, i, x):
        if i < 0:
             i = len(self) + i 
        return libgsl.gsl_vector_uchar_set(self.ptr, i, x)

    def set_all(self, x = 0):
        libgsl.gsl_vector_uchar_set_all(self.ptr, x)
    def set_zero(self):
        libgsl.gsl_vector_uchar_set_zero(self.ptr)
    def set_basis(self, i):
        libgsl.gsl_vector_uchar_set_basis(self.ptr, i)

    def subvector(self, offset, n, stride = None):
        return vector_uchar_view(self, offset, n, stride)

    
    

    def copy(self):
        new_v = vector_uchar(len(self))
        libgsl.gsl_vector_uchar_memcpy(new_v.ptr, self.ptr)
        return new_v
    def swap(self, other):
        libgsl.gsl_vector_uchar_swap(self.ptr, other.ptr)

    def swap_elements(self, i, j):
        libgsl.gsl_vector_uchar_swap_elements(self.ptr, i, j)
    def reverse(self):
        libgsl.gsl_vector_uchar_reverse(self.ptr)

    

    

    def isnull(self):
        return libgsl.gsl_vector_uchar_isnull(self.ptr)
    


class vector_uchar_view(vector_uchar):
    def __init__(self, vector, offset, n, stride = None, _view = None):
        self.ref = vector # prevent deallocation of vector until the
                          # view is there
        if _view is not None:
            view = _view
        elif stride is None:
            view = libgsl.gsl_vector_uchar_subvector(vector.ptr, offset, n)
        else:
            view = libgsl.gsl_vector_uchar_subvector_with_stride(vector.ptr, offset, stride, n)
        self.ptr = cast(pointer(view), POINTER(gsl_vector_uchar))
    def __del__(self):
        # don't need to free any memory
        pass


class _vector_uchar_view_from_gsl(vector_uchar):
    def __init__(self, gsl_vector_ptr):
        self.ptr = gsl_vector_ptr
    def __del__(self):
        # don't need to free any memory
        pass


