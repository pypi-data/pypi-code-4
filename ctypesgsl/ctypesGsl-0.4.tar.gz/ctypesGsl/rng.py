from utils import *
from utils import _set_types, _add_function
from utils import _gsl_check_status, _gsl_check_null_pointer

# types of random number generators
class gsl_rng_type(Structure):
    _fields_ = [("name", c_char_p)]
_RNG_TYPE_PTR = POINTER(gsl_rng_type)

# get rng types
_set_types("rng_types_setup", POINTER(_RNG_TYPE_PTR), [])
rng_types = []
_types_ptr = libgsl.gsl_rng_types_setup()
_i = 0
while bool(_types_ptr[_i]):
    _Tp = _types_ptr[_i]
    rng_types.append(_Tp.contents)
    _i += 1

# add pointers to available types to current namespace
for _T in rng_types:
    _name = _T.name.replace("-", "_") # ugly hack
    globals()["rng_" + _name] = _RNG_TYPE_PTR.in_dll(libgsl, "gsl_rng_" + _name)



class gsl_rng(Structure):
    pass

_add_function("rng_env_setup", None, [], globals())

_set_types("rng_alloc", POINTER(gsl_rng), [_RNG_TYPE_PTR])
_set_types("rng_free", None, [POINTER(gsl_rng)])
_set_types("rng_set", None, [POINTER(gsl_rng), c_ulong])

_set_types("rng_get", c_ulong, [POINTER(gsl_rng)])
_set_types("rng_uniform", c_double, [POINTER(gsl_rng)])
_set_types("rng_uniform_pos", c_double, [POINTER(gsl_rng)])
_set_types("rng_uniform_int", c_ulong, [POINTER(gsl_rng), c_ulong])

_set_types("rng_name", c_char_p, [POINTER(gsl_rng)])
_set_types("rng_max", c_ulong, [POINTER(gsl_rng)])
_set_types("rng_min", c_ulong, [POINTER(gsl_rng)])

_set_types("rng_clone", POINTER(gsl_rng), [POINTER(gsl_rng)])
_set_types("rng_memcpy", _gsl_check_status, [POINTER(gsl_rng), POINTER(gsl_rng)])

class rng(object):
    def __init__(self, T = None, _gsl_rng = None):
        self.libgsl = libgsl
        if _gsl_rng is not None:
            self.ptr = _gsl_rng
        else:
            if T is None:
                T = _RNG_TYPE_PTR.in_dll(libgsl, "gsl_rng_default")
            self.type = T
            self.ptr = libgsl.gsl_rng_alloc(T)
            _gsl_check_null_pointer(self.ptr)
        self.name = libgsl.gsl_rng_name(self.ptr)
        self.max = libgsl.gsl_rng_max(self.ptr)
        self.min = libgsl.gsl_rng_min(self.ptr)
        self._as_parameter_ = self.ptr
    def __del__(self):
        self.libgsl.gsl_rng_free(self.ptr)
    def clone(self):
        new_ptr = libgsl.gsl_rng_clone(self.ptr)
        _gsl_check_null_pointer(new_ptr)
        new_rng = rng(_gsl_rng = new_ptr)
        new_rng.type = self.type
        return new_rng
    def set(self, seed = 0):
        libgsl.gsl_rng_set(self.ptr, seed)

    def get(self):
        return libgsl.gsl_rng_get(self.ptr)
    def uniform(self):
        return libgsl.gsl_rng_uniform(self.ptr)
    def __call__(self):
        return self.uniform()
    def uniform_pos(self):
        return libgsl.gsl_rng_uniform_pos(self.ptr)
    def uniform_int(self, n):
        return libgsl.gsl_rng_uniform_int(self.ptr, n)

