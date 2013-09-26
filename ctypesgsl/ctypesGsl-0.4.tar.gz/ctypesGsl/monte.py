"""Monte Carlo integration."""

from utils import *
from utils import _set_types, _add_function, _gsl_return_to_bool
from utils import _gsl_check_null_pointer, _gsl_check_status

from rng import gsl_rng, rng

# function to integrate

_GSL_MONTE_FUNCTION_TYPE = CFUNCTYPE(c_double, POINTER(c_double), c_size_t, py_object)


class gsl_monte_function(Structure):
    _fields_ = [("f", _GSL_MONTE_FUNCTION_TYPE),
                ("dim", c_size_t),
                ("params", py_object)]
    def __init__(self, f, dim, params = None):
        self._python_f = f
        self.dim = dim
        if params is None:
            ctypes_f = self._wrap_f_no_param
        else:
            ctypes_f = self._wrap_f
        Structure.__init__(self, _GSL_MONTE_FUNCTION_TYPE(ctypes_f), dim, params)
    def _wrap_f(self, x, dim, params):
        return self._python_f(x, params)
    def _wrap_f_no_param(self, x, dim, params):
        return self._python_f(x)
    def __call__(self, x):
        x_c = (c_double * self.dim)(*x)
        return self.f(x_c, self.dim, self.params)


class gsl_monte_plain_state(Structure):
    pass
_set_types("monte_plain_alloc", POINTER(gsl_monte_plain_state), [c_size_t])
_set_types("monte_plain_init", _gsl_check_status, [POINTER(gsl_monte_plain_state)])
_set_types("monte_plain_free", None, [POINTER(gsl_monte_plain_state)])
class monte_plain_state:
    def __init__(self, dim):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_monte_plain_alloc(dim)
        _gsl_check_null_pointer(self.ptr)
        self.dim = dim
    def init(self):
        """Reinitialize workspace"""
        libgsl.gsl_monte_plain_init(self.ptr)
    def __del__(self):
        self.libgsl.gsl_monte_plain_free(self.ptr)

_set_types("monte_plain_integrate", _gsl_check_status,
           [POINTER(gsl_monte_function), POINTER(c_double), POINTER(c_double),
            c_size_t, c_size_t,
            POINTER(gsl_rng),
            POINTER(gsl_monte_plain_state),
            POINTER(c_double), POINTER(c_double)])
def monte_plain_integrate(f, xl, xu, calls = 100000, r = None, state = None):
    dim = f.dim
    xl_c = (c_double * dim)(*xl)
    xu_c = (c_double * dim)(*xu)
    if r is None:
        r = rng()
    if state is None:
        state = monte_plain_state(dim)
    result = c_double()
    abserr = c_double()
    status = libgsl.gsl_monte_plain_integrate(f, xl_c, xu_c, dim, calls, r.ptr, state.ptr, byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res


class gsl_monte_miser_state(Structure):
    _fields_ = [("min_calls", c_size_t),
                ("min_calls_per_bisection", c_size_t),
                ("dither", c_double),
                ("estimate_frac", c_double),
                ("alpha", c_double)]
_set_types("monte_miser_alloc", POINTER(gsl_monte_miser_state), [c_size_t])
_set_types("monte_miser_init", _gsl_check_status, [POINTER(gsl_monte_miser_state)])
_set_types("monte_miser_free", None, [POINTER(gsl_monte_miser_state)])
class monte_miser_state:
    def __init__(self, dim, min_calls = None, min_calls_per_bisection = None,
                 dither = None, estimate_frac = None, alpha = None):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_monte_miser_alloc(dim)
        _gsl_check_null_pointer(self.ptr)
        if min_calls is not None:
            self.ptr.contents.min_calls = min_calls
        if min_calls_per_bisection is not None:
            self.ptr.contents.min_calls_per_bisection = min_calls_per_bisection
        if dither is not None:
            self.ptr.contents.dither = dither
        if estimate_frac is not None:
            self.ptr.contents.estimate_frac = estimate_frac
        if alpha is not None:
            self.ptr.contents.alpha = alpha
        self.dim = dim
    def init(self):
        """Reinitialize workspace"""
        libgsl.gsl_monte_miser_init(self.ptr)
    def __del__(self):
        self.libgsl.gsl_monte_miser_free(self.ptr)

_set_types("monte_miser_integrate", _gsl_check_status,
           [POINTER(gsl_monte_function), POINTER(c_double), POINTER(c_double),
            c_size_t, c_size_t,
            POINTER(gsl_rng),
            POINTER(gsl_monte_miser_state),
            POINTER(c_double), POINTER(c_double)])
def monte_miser_integrate(f, xl, xu, calls = 100000, r = None, state = None,
                          min_calls = None, min_calls_per_bisection = None,
                          dither = None, estimate_frac = None, alpha = None):
    dim = f.dim
    xl_c = (c_double * dim)(*xl)
    xu_c = (c_double * dim)(*xu)
    if r is None:
        r = rng()
    if state is None:
        state = monte_miser_state(dim, min_calls, min_calls_per_bisection, dither, estimate_frac, alpha)
    result = c_double()
    abserr = c_double()
    status = libgsl.gsl_monte_miser_integrate(f, xl_c, xu_c, dim, calls, r.ptr, state.ptr, byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res



class gsl_monte_vegas_state(Structure):
    pass
_set_types("monte_vegas_alloc", POINTER(gsl_monte_vegas_state), [c_size_t])
_set_types("monte_vegas_init", _gsl_check_status, [POINTER(gsl_monte_vegas_state)])
_set_types("monte_vegas_free", None, [POINTER(gsl_monte_vegas_state)])

# VEGAS state parameters are at the end of state structure, so it is risky to set them here...
# anyway, defaults seem to work fine
class monte_vegas_state:
    def __init__(self, dim):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_monte_vegas_alloc(dim)
        _gsl_check_null_pointer(self.ptr)
        self.dim = dim
    def init(self):
        """Reinitialize workspace"""
        libgsl.gsl_monte_vegas_init(self.ptr)
    def __del__(self):
        self.libgsl.gsl_monte_vegas_free(self.ptr)

_set_types("monte_vegas_integrate", _gsl_check_status,
           [POINTER(gsl_monte_function), POINTER(c_double), POINTER(c_double),
            c_size_t, c_size_t,
            POINTER(gsl_rng),
            POINTER(gsl_monte_vegas_state),
            POINTER(c_double), POINTER(c_double)])
def monte_vegas_integrate(f, xl, xu, calls = 100000, r = None, state = None):
    dim = f.dim
    xl_c = (c_double * dim)(*xl)
    xu_c = (c_double * dim)(*xu)
    if r is None:
        r = rng()
    if state is None:
        state = monte_vegas_state(dim)
    result = c_double()
    abserr = c_double()
    status = libgsl.gsl_monte_vegas_integrate(f, xl_c, xu_c, dim, calls, r.ptr, state.ptr, byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

