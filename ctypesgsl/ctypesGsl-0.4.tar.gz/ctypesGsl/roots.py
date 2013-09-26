"""One dimensional root finding."""

from utils import *
from utils import _set_types, _add_function, _gsl_return_to_bool
from utils import _gsl_check_null_pointer, _gsl_check_status

from basic import GSL_POSINF

#### ONE DIMENSIONAL ROOT FINDING


# types of root finders
class gsl_root_fsolver_type(Structure):
    pass
_FSOLVER_TYPE_PTR = POINTER(gsl_root_fsolver_type)
class gsl_root_fdfsolver_type(Structure):
    pass
_FDFSOLVER_TYPE_PTR = POINTER(gsl_root_fdfsolver_type)

root_fsolver_bisection    = _FSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fsolver_bisection")
root_fsolver_falsepos     = _FSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fsolver_falsepos")
root_fsolver_brent        = _FSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fsolver_brent")

root_fdfsolver_newton     = _FDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fdfsolver_newton")
root_fdfsolver_secant     = _FDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fdfsolver_secant")
root_fdfsolver_steffenson = _FDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_root_fdfsolver_steffenson")


# stopping condition tests
_add_function("root_test_interval", _gsl_return_to_bool, [c_double, c_double, c_double, c_double], globals())
_add_function("root_test_delta", _gsl_return_to_bool, [c_double, c_double, c_double, c_double], globals())
_add_function("root_test_residual", _gsl_return_to_bool, [c_double, c_double], globals())

# interval root finder class
class gsl_root_fsolver(Structure):
    pass
_set_types("root_fsolver_alloc", POINTER(gsl_root_fsolver), [_FSOLVER_TYPE_PTR])
_set_types("root_fsolver_free", None, [POINTER(gsl_root_fsolver)])
_set_types("root_fsolver_set", _gsl_check_status, [POINTER(gsl_root_fsolver), POINTER(gsl_function), c_double, c_double])
_set_types("root_fsolver_iterate", _gsl_check_status, [POINTER(gsl_root_fsolver)])
_set_types("root_fsolver_root", c_double, [POINTER(gsl_root_fsolver)])
_set_types("root_fsolver_x_lower", c_double, [POINTER(gsl_root_fsolver)])
_set_types("root_fsolver_x_upper", c_double, [POINTER(gsl_root_fsolver)])

class root_fsolver:
    def __init__(self, type, gsl_func):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_root_fsolver_alloc(type)
        _gsl_check_null_pointer(self.ptr)
        self.func = gsl_func
    def __del__(self):
        self.libgsl.gsl_root_fsolver_free(self.ptr)
    def init(self, a, b):
        """Set initial root finding bracket."""
        libgsl.gsl_root_fsolver_set(self.ptr, self.func, a, b)
    def iterate(self):
        libgsl.gsl_root_fsolver_iterate(self.ptr)
    def root(self):
        return libgsl.gsl_root_fsolver_root(self.ptr)
    def lower(self):
        return libgsl.gsl_root_fsolver_x_lower(self.ptr)
    def upper(self):
        return libgsl.gsl_root_fsolver_x_upper(self.ptr)
    def bracket(self):
        return (self.lower(), self.upper())
    def test_interval(self, epsabs, epsrel):
        return root_test_interval(self.lower(), self.upper(), epsabs, epsrel)


# derivative based root finder class
class gsl_root_fdfsolver(Structure):
    pass
_set_types("root_fdfsolver_alloc", POINTER(gsl_root_fdfsolver), [_FDFSOLVER_TYPE_PTR])
_set_types("root_fdfsolver_free", None, [POINTER(gsl_root_fdfsolver)])
_set_types("root_fdfsolver_set", _gsl_check_status, [POINTER(gsl_root_fdfsolver), POINTER(gsl_function_fdf), c_double])
_set_types("root_fdfsolver_iterate", _gsl_check_status, [POINTER(gsl_root_fdfsolver)])
_set_types("root_fdfsolver_root", c_double, [POINTER(gsl_root_fdfsolver)])

class root_fdfsolver:
    def __init__(self, type, gsl_func):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_root_fdfsolver_alloc(type)
        _gsl_check_null_pointer(self.ptr)
        self.func = gsl_func
    def __del__(self):
        self.libgsl.gsl_root_fdfsolver_free(self.ptr)
    def init(self, x):
        """Set initial root finding guess."""
        self.x_prev = None
        libgsl.gsl_root_fdfsolver_set(self.ptr, self.func, x)
    def iterate(self):
        self.x_prev = self.root()
        libgsl.gsl_root_fdfsolver_iterate(self.ptr)
    def root(self):
        return libgsl.gsl_root_fdfsolver_root(self.ptr)
    def last_step_width(self):
        """Returns the difference between current and previous value.

        Can be used as error estimate.  If no previous guess is
        available, returns inf."""
        if self.x_prev is None:
            return GSL_POSINF
        return self.root() - self.x_prev
    def test_delta(self, epsabs, epsrel):
        if self.x_prev is None:
            return False
        return root_test_delta(self.root(), self.x_prev, epsabs, epsrel)


