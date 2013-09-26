"""One dimensional minimization."""

from utils import *
from utils import _set_types, _add_function, _gsl_return_to_bool
from utils import _gsl_check_null_pointer, _gsl_check_status

#### ONE DIMENSIONAL MINIMIZATION


# types of minimizers
class gsl_min_fminimizer_type(Structure):
    pass
_FMINIMIZER_TYPE_PTR = POINTER(gsl_min_fminimizer_type)

min_fminimizer_goldensection = _FMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_min_fminimizer_goldensection")
min_fminimizer_brent         = _FMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_min_fminimizer_brent")


# minimizer class
class gsl_min_fminimizer(Structure):
    pass
_set_types("min_fminimizer_alloc", POINTER(gsl_min_fminimizer), [_FMINIMIZER_TYPE_PTR])
_set_types("min_fminimizer_free", None, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_set", _gsl_check_status, [POINTER(gsl_min_fminimizer), POINTER(gsl_function), c_double, c_double, c_double])
_set_types("min_fminimizer_iterate", _gsl_check_status, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_x_minimum", c_double, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_x_lower", c_double, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_x_upper", c_double, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_f_minimum", c_double, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_f_lower", c_double, [POINTER(gsl_min_fminimizer)])
_set_types("min_fminimizer_f_upper", c_double, [POINTER(gsl_min_fminimizer)])

_add_function("min_test_interval", _gsl_return_to_bool, [c_double, c_double, c_double, c_double], globals())

class min_fminimizer:
    def __init__(self, type, gsl_func):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_min_fminimizer_alloc(type)
        _gsl_check_null_pointer(self.ptr)
        self.func = gsl_func
    def __del__(self):
        self.libgsl.gsl_min_fminimizer_free(self.ptr)
    def init(self, x_guess, a, b):
        """Set initial minimization bounds."""
        libgsl.gsl_min_fminimizer_set(self.ptr, self.func, x_guess, a, b)
    def iterate(self):
        libgsl.gsl_min_fminimizer_iterate(self.ptr)
    def x_minimum(self):
        return libgsl.gsl_min_fminimizer_x_minimum(self.ptr)
    def f_minimum(self):
        return libgsl.gsl_min_fminimizer_f_minimum(self.ptr)
    def lower(self):
        return libgsl.gsl_min_fminimizer_x_lower(self.ptr)
    def upper(self):
        return libgsl.gsl_min_fminimizer_x_upper(self.ptr)
    def bracket(self):
        return (self.lower(), self.upper())
    def test_interval(self, epsabs, epsrel):
        return min_test_interval(self.lower(), self.upper(), epsabs, epsrel)

