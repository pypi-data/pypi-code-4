from utils import *
from utils import _set_types, _add_function
from utils import _gsl_check_status, _gsl_check_null_pointer

# types of random number generators
class gsl_qrng_type(Structure):
    #_fields_ = [("name", c_char_p)]
    pass
_QRNG_TYPE_PTR = POINTER(gsl_qrng_type)


# add pointers to available types to current namespace
qrng_niederreiter_2 = _QRNG_TYPE_PTR.in_dll(libgsl, "gsl_qrng_niederreiter_2")
qrng_sobol = _QRNG_TYPE_PTR.in_dll(libgsl, "gsl_qrng_sobol")


class gsl_qrng(Structure):
    pass


_set_types("qrng_alloc", POINTER(gsl_qrng), [_QRNG_TYPE_PTR])
_set_types("qrng_free", None, [POINTER(gsl_qrng)])
_set_types("qrng_init", None, [POINTER(gsl_qrng)])

_set_types("qrng_get", _gsl_check_status, [POINTER(gsl_qrng), POINTER(c_double)])

_set_types("qrng_name", c_char_p, [POINTER(gsl_qrng)])

_set_types("qrng_clone", POINTER(gsl_qrng), [POINTER(gsl_qrng)])
_set_types("qrng_memcpy", _gsl_check_status, [POINTER(gsl_qrng), POINTER(gsl_qrng)])

class qrng(object):
    def __init__(self, T, d, _gsl_qrng = None):
        self.libgsl = libgsl
        if _gsl_qrng is not None:
            self.ptr = _gsl_qrng
        else:
            self.type = T
            self.d = d
            self.x = (c_double * d)()
            _gsl_check_null_pointer(self.x)
            self.ptr = libgsl.gsl_qrng_alloc(T, d)
            _gsl_check_null_pointer(self.ptr)
        self.name = libgsl.gsl_qrng_name(self.ptr)
    def __del__(self):
        self.libgsl.gsl_qrng_free(self.ptr)
    def clone(self):
        new_ptr = libgsl.gsl_qrng_clone(self.ptr)
        _gsl_check_null_pointer(new_ptr)
        new_qrng = qrng(None, None, _gsl_qrng = new_ptr)
        new_qrng.type = self.type
        new_qrng.d = self.d
        new_qrng.x = (c_double * self.d)()
        return new_qrng
    def init(self):
        libgsl.gsl_qrng_init(self.ptr)

    def get(self):
        libgsl.gsl_qrng_get(self.ptr, self.x)
        return list(self.x)
    def __call__(self):
        return self.get()
