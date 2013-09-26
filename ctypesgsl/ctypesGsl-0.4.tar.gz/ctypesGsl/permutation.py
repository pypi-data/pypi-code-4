from utils import *
from utils import _set_types, _gsl_return_to_bool, _add_method
from utils import _gsl_check_status, _gsl_check_null_pointer

class gsl_permutation(Structure):
    _fields_ = [("size", c_size_t),
                ("data", POINTER(c_size_t))]

_set_types("permutation_calloc", POINTER(gsl_permutation), [c_size_t])
_set_types("permutation_free", None, [POINTER(gsl_permutation)])
_set_types("permutation_size", c_size_t, [POINTER(gsl_permutation)])
_set_types("permutation_memcpy", _gsl_check_status, [POINTER(gsl_permutation),
                                                              POINTER(gsl_permutation)])
_set_types("permutation_get", c_size_t, [POINTER(gsl_permutation), c_size_t])
_set_types("permutation_swap", _gsl_check_status, [POINTER(gsl_permutation), c_size_t, c_size_t])
_set_types("permutation_data", POINTER(c_size_t), [POINTER(gsl_permutation)])
_set_types("permutation_inverse", _gsl_check_status, [POINTER(gsl_permutation), POINTER(gsl_permutation)])
_set_types("permutation_next", _gsl_return_to_bool, [POINTER(gsl_permutation)])
_set_types("permutation_prev", _gsl_return_to_bool, [POINTER(gsl_permutation)])

class permutation(object):
    def __init__(self, n):
        self.libgsl = libgsl
        self.n = n
        self.ptr = libgsl.gsl_permutation_calloc(n)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_permutation_free(self.ptr)
    def __len__(self):
        return int(libgsl.gsl_permutation_size(self.ptr))
    def copy(self):
        new_p = permutation(len(self))
        libgsl.gsl_permutation_memcpy(new_p.ptr, self.ptr)
        return new_p
    def __getitem__(self, i):
        if i >= self.n:
            raise IndexError
        return libgsl.gsl_permutation_get(self.ptr, i)
    def swap(self, i, j):
        libgsl.gsl_permutation_swap(self.ptr, i, j)
    def as_list(self):
        raw_data = libgsl.gsl_permutation_data(self.ptr)
        return raw_data[0:len(self)]
    def __str__(self):
        return "permutation([" + ", ".join([str(x) for x in self]) + "])"
    def inverse(self):
        new_p = permutation(len(self))
        libgsl.gsl_permutation_inverse(new_p.ptr, self.ptr)
        return new_p
    def next(self):
        return libgsl.gsl_permutation_next(self.ptr)
    def prev(self):
        return libgsl.gsl_permutation_prev(self.ptr)
    def iterperm(self):
        """Iterate all successive permutations beginning with self."""
        def p_iter(p):
            yield p
            while(p.next()):
                yield p
        return p_iter(self)
    # TODO: more methods
_add_method(permutation, "permutation_init", None, [])
_add_method(permutation, "permutation_valid", _gsl_return_to_bool, [])
_add_method(permutation, "permutation_reverse", None, [])

