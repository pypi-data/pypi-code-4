from utils import *
from utils import _set_types, _gsl_return_to_bool, _add_method
from utils import _gsl_check_status, _gsl_check_null_pointer

class gsl_combination(Structure):
    _fields_ = [("n", c_size_t),
                ("k", c_size_t),
                ("data", POINTER(c_size_t))]

_set_types("combination_alloc", POINTER(gsl_combination), [c_size_t])
_set_types("combination_calloc", POINTER(gsl_combination), [c_size_t])
_set_types("combination_free", None, [POINTER(gsl_combination)])
_set_types("combination_n", c_size_t, [POINTER(gsl_combination)])
_set_types("combination_k", c_size_t, [POINTER(gsl_combination)])
_set_types("combination_memcpy", _gsl_check_status, [POINTER(gsl_combination),
                                                              POINTER(gsl_combination)])
_set_types("combination_get", c_size_t, [POINTER(gsl_combination), c_size_t])
_set_types("combination_data", POINTER(c_size_t), [POINTER(gsl_combination)])
_set_types("combination_next", _gsl_return_to_bool, [POINTER(gsl_combination)])
_set_types("combination_prev", _gsl_return_to_bool, [POINTER(gsl_combination)])

class combination(object):
    def __init__(self, n, k):
        self.libgsl = libgsl
        self.n = n
        self.k = k
        self.ptr = libgsl.gsl_combination_calloc(n, k)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_combination_free(self.ptr)
    def __len__(self):
        return self.k
    def copy(self):
        new_p = combination(len(self))
        libgsl.gsl_combination_memcpy(new_p.ptr, self.ptr)
        return new_p
    def __getitem__(self, i):
        if i >= self.k:
            raise IndexError
        return libgsl.gsl_combination_get(self.ptr, i)
    def as_list(self):
        raw_data = libgsl.gsl_combination_data(self.ptr)
        return raw_data[0:len(self)]
    def __str__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"
    def next(self):
        return libgsl.gsl_combination_next(self.ptr)
    def prev(self):
        return libgsl.gsl_combination_prev(self.ptr)
    def itercomb(self):
        """Iterate all successive combinations beginning with self."""
        def c_iter(c):
            yield c
            while(c.next()):
                yield c
        return c_iter(self)

_add_method(combination, "combination_init_first", None, [], method_name = "init_first")
_add_method(combination, "combination_init_last", None, [], method_name = "init_last")
_add_method(combination, "combination_valid", _gsl_return_to_bool, [])

