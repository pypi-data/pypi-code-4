from utils import *
from utils import _set_types
from utils import _gsl_check_status, _gsl_check_null_pointer


class gsl_cheb_series(Structure):
    pass

_set_types("cheb_alloc", POINTER(gsl_cheb_series), [c_size_t])
_set_types("cheb_free", None, [POINTER(gsl_cheb_series)])
_set_types("cheb_init", _gsl_check_status, [POINTER(gsl_cheb_series),
                                                     POINTER(gsl_function),
                                                     c_double, c_double])
_set_types("cheb_eval", c_double, [POINTER(gsl_cheb_series), c_double])
_set_types("cheb_eval_err", c_int, [POINTER(gsl_cheb_series), c_double,
                                             POINTER(c_double), POINTER(c_double)])
_set_types("cheb_eval_n", c_double, [POINTER(gsl_cheb_series), c_size_t, c_double])
_set_types("cheb_eval_n_err", c_int, [POINTER(gsl_cheb_series),
                                               c_size_t, c_double,
                                               POINTER(c_double), POINTER(c_double)])
_set_types("cheb_calc_deriv", _gsl_check_status, [POINTER(gsl_cheb_series),
                                                      POINTER(gsl_cheb_series)])
_set_types("cheb_calc_integ", _gsl_check_status, [POINTER(gsl_cheb_series),
                                                      POINTER(gsl_cheb_series)])


class cheb_series:
    def __init__(self, n = 10, f = None, a = -1, b = 1):
        self.n = n
        self.libgsl = libgsl # help during __del__
        self.ptr = libgsl.gsl_cheb_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.init(f, a, b)
    def __del__(self):
        self.libgsl.gsl_cheb_free(self.ptr)
    def init(self, f, a = -1, b = 1):
        self.function = f
        self.a = a
        self.b = b
        if f is not None:
            libgsl.gsl_cheb_init(self.ptr, f, a, b)

    def __call__(self, x):
        return libgsl.gsl_cheb_eval(self.ptr, x)
    def eval(self, x):
        return libgsl.gsl_cheb_eval(self.ptr, x)
    def eval_n(self, n, x):
        return libgsl.gsl_cheb_eval_n(self.ptr, n, x)
    def eval_err(self, x):
        result = c_double()
        err    = c_double()
        status = libgsl.gsl_cheb_eval_err(self.ptr, x, byref(result), byref(err))
        res = (result.value, err.value)
        _gsl_check_status(status, result = res)
        return res
    def eval_n_err(self, n, x):
        result = c_double()
        err    = c_double()
        status = libgsl.gsl_cheb_eval_n_err(self.ptr, n, x, byref(result), byref(err))
        res = (result.value, err.value)
        _gsl_check_status(status, result = res)
        return res

    def deriv(self):
        deriv = cheb_series(self.n)
        libgsl.gsl_cheb_calc_deriv(deriv.ptr, self.ptr)
        return deriv
    def integ(self):
        integ = cheb_series(self.n)
        libgsl.gsl_cheb_calc_integ(integ.ptr, self.ptr)
        return integ

    
