"""Multidimensional minimization."""

from utils import *
from utils import _set_types, _add_function, _gsl_return_to_bool
from utils import _gsl_check_null_pointer, _gsl_check_status

from vector import gsl_vector, _vector_view_from_gsl, vector

# function to minimize

_GSL_MULTIMIN_F_TYPE   = CFUNCTYPE(c_double, POINTER(gsl_vector), py_object)
_GSL_MULTIMIN_DF_TYPE  = CFUNCTYPE(None, POINTER(gsl_vector), py_object, POINTER(gsl_vector))
_GSL_MULTIMIN_FDF_TYPE = CFUNCTYPE(None, POINTER(gsl_vector), py_object, POINTER(c_double), POINTER(gsl_vector))

class gsl_multimin_function(Structure):
    _fields_ = [("function", _GSL_MULTIMIN_F_TYPE),
                ("n", c_size_t),
                ("params", py_object)]
    def __init__(self, f, n, params = None):
        self._python_f = f
        self.n = n
        if params is None:
            ctypes_f = self._wrap_f_no_param
        else:
            ctypes_f = self._wrap_f
        Structure.__init__(self, _GSL_MULTIMIN_F_TYPE(ctypes_f), n, params)
    def _wrap_f(self, x, params):
        return self._python_f(_vector_view_from_gsl(x),
                              params)
    def _wrap_f_no_param(self, x, params):
        return self._python_f(_vector_view_from_gsl(x))
    def __call__(self, x):
        return self.function(x.ptr, self.params)



class gsl_multimin_function_fdf(Structure):
    _fields_ = [("f",   _GSL_MULTIMIN_F_TYPE),
                ("df" , _GSL_MULTIMIN_DF_TYPE),
                ("fdf", _GSL_MULTIMIN_FDF_TYPE),
                ("n", c_size_t),
                ("params", py_object)]
    def __init__(self, f, df, fdf, n, params = None):
        """fdf can be None."""
        self._python_f = f
        self._python_df = df
        if fdf is None:
            if params is None:
                self._python_fdf = self._default_fdf_no_param
            else:
                self._python_fdf = self._default_fdf
        else:
            self._python_fdf = fdf
        if params is None:
            ctypes_f   = self._wrap_f_no_param
            ctypes_df  = self._wrap_df_no_param
            ctypes_fdf = self._wrap_fdf_no_param
        else:
            ctypes_f   = self._wrap_f
            ctypes_df  = self._wrap_df
            ctypes_fdf = self._wrap_fdf
        Structure.__init__(self,
                           _GSL_MULTIMIN_F_TYPE(ctypes_f),
                           _GSL_MULTIMIN_DF_TYPE(ctypes_df),
                           _GSL_MULTIMIN_FDF_TYPE(ctypes_fdf),
                           n, params)
    def _wrap_f(self, x, _params):
        return self._python_f(_vector_view_from_gsl(x), _params)
    def _wrap_f_no_param(self, x, _params):
        return self._python_f(_vector_view_from_gsl(x))
    def _wrap_df(self, x, _params, df):
        return self._python_df(_vector_view_from_gsl(x),
                               _params,
                               _vector_view_from_gsl(df))
    def _wrap_df_no_param(self, x, _params, df):
        return self._python_df(_vector_view_from_gsl(x),
                               _vector_view_from_gsl(df))
    def _wrap_fdf(self, x, _params, f, df):
        f.contents.value =  self._python_fdf(_vector_view_from_gsl(x),
                                             _params,
                                             _vector_view_from_gsl(df))
    def _wrap_fdf_no_param(self, x, _params, f, df):
        f.contents.value = self._python_fdf(_vector_view_from_gsl(x),
                                            _vector_view_from_gsl(df))

    def _default_fdf(self, x, _params, df):
        """compute fdf using f and df"""
        ##f.contents.value = self._python_f(x, _params)
        self._python_df(x, _params, df)
        return self._python_f(x, _params)
    def _default_fdf_no_param(self, x, df):
        """compute fdf using f and df"""
        ##f.contents.value = self._python_f(x)
        self._python_df(x, df)
        return self._python_f(x)

    def eval_f(self, x):
        return self.f(x.ptr, self.params)
    def eval_df(self, x):
        df = vector(self.n)
        self.df(x.ptr, self.params, df.ptr)
        return df
    def eval_fdf(self, x):
        f = c_double()
        df = vector(self.n)
        self.fdf(x.ptr, self.params, byref(f), df.ptr)
        return f.value, df
    def __call__(self, x):
        return self.eval_fdf(x)



# types of minimizers
class gsl_multimin_fminimizer_type(Structure):
    pass
_MULTIFMINIMIZER_TYPE_PTR = POINTER(gsl_multimin_fminimizer_type)
class gsl_multimin_fdfminimizer_type(Structure):
    pass
_MULTIFDFMINIMIZER_TYPE_PTR = POINTER(gsl_multimin_fdfminimizer_type)

multimin_fdfminimizer_conjugate_fr     = _MULTIFDFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fdfminimizer_conjugate_fr")
multimin_fdfminimizer_conjugate_pr     = _MULTIFDFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fdfminimizer_conjugate_pr")
#multimin_fdfminimizer_vector_bfgs2     = _MULTIFDFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fdfminimizer_vector_bfgs2")
multimin_fdfminimizer_vector_bfgs      = _MULTIFDFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fdfminimizer_vector_bfgs")
multimin_fdfminimizer_steepest_descent = _MULTIFDFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fdfminimizer_steepest_descent")

multimin_fminimizer_nmsimplex = _MULTIFMINIMIZER_TYPE_PTR.in_dll(libgsl, "gsl_multimin_fminimizer_nmsimplex")


# stopping condition tests
_add_function("multimin_test_gradient", _gsl_return_to_bool,
              [POINTER(gsl_vector), c_double], globals())
_add_function("multimin_test_size", _gsl_return_to_bool,
              [c_double, c_double], globals())


class gsl_multimin_fminimizer(Structure):
    pass
_set_types("multimin_fminimizer_alloc", POINTER(gsl_multimin_fminimizer), [_MULTIFMINIMIZER_TYPE_PTR])
_set_types("multimin_fminimizer_free", None, [POINTER(gsl_multimin_fminimizer)])
_set_types("multimin_fminimizer_set", _gsl_check_status,
           [POINTER(gsl_multimin_fminimizer),
            POINTER(gsl_multimin_function),
            POINTER(gsl_vector), POINTER(gsl_vector)])
_set_types("multimin_fminimizer_iterate", _gsl_check_status, [POINTER(gsl_multimin_fminimizer)])
_set_types("multimin_fminimizer_x", POINTER(gsl_vector), [POINTER(gsl_multimin_fminimizer)])
_set_types("multimin_fminimizer_minimum", c_double, [POINTER(gsl_multimin_fminimizer)])
_set_types("multimin_fminimizer_size", c_double, [POINTER(gsl_multimin_fminimizer)])


class multimin_fminimizer:
    def __init__(self, type, multi_func):
        self.libgsl = libgsl # helper for __del__
        self.func = multi_func
        self.ptr = libgsl.gsl_multimin_fminimizer_alloc(type, self.func.n)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_multimin_fminimizer_free(self.ptr)
    def init(self, x, stepsize = None):
        """Set initial minimum and step sizes vector"""
        if stepsize is None:
            stepsize = vector([0.1] * self.func.n)
        libgsl.gsl_multimin_fminimizer_set(self.ptr, self.func, x.ptr, stepsize.ptr)
    def iterate(self):
        libgsl.gsl_multimin_fminimizer_iterate(self.ptr)
    def x(self):
        x = libgsl.gsl_multimin_fminimizer_x(self.ptr)
        return _vector_view_from_gsl(x)
    def minimum(self):
        return libgsl.gsl_multimin_fminimizer_minimum(self.ptr)
    def size(self):
        return libgsl.gsl_multimin_fminimizer_size(self.ptr)

    def test_size(self, epsabs):
        s  = libgsl.gsl_multimin_fminimizer_size(self.ptr)
        return libgsl.gsl_multimin_test_size(s, epsabs)


class gsl_multimin_fdfminimizer(Structure):
    pass
_set_types("multimin_fdfminimizer_alloc", POINTER(gsl_multimin_fdfminimizer), [_MULTIFDFMINIMIZER_TYPE_PTR])
_set_types("multimin_fdfminimizer_free", None, [POINTER(gsl_multimin_fdfminimizer)])
_set_types("multimin_fdfminimizer_set", _gsl_check_status,
           [POINTER(gsl_multimin_fdfminimizer),
            POINTER(gsl_multimin_function_fdf),
            POINTER(gsl_vector), c_double, c_double])
_set_types("multimin_fdfminimizer_iterate", _gsl_check_status, [POINTER(gsl_multimin_fdfminimizer)])
_set_types("multimin_fdfminimizer_x", POINTER(gsl_vector), [POINTER(gsl_multimin_fdfminimizer)])
_set_types("multimin_fdfminimizer_minimum", c_double, [POINTER(gsl_multimin_fdfminimizer)])
_set_types("multimin_fdfminimizer_gradient", POINTER(gsl_vector), [POINTER(gsl_multimin_fdfminimizer)])

_set_types("multimin_fdfminimizer_restart", _gsl_check_status, [POINTER(gsl_multimin_fdfminimizer)])

class multimin_fdfminimizer:
    def __init__(self, type, multi_fdffunc):
        self.libgsl = libgsl # helper for __del__
        self.func = multi_fdffunc
        self.ptr = libgsl.gsl_multimin_fdfminimizer_alloc(type, self.func.n)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_multimin_fdfminimizer_free(self.ptr)
    def init(self, x, step_size, tol = 0.1):
        """Set starting point and tolerances."""
        libgsl.gsl_multimin_fdfminimizer_set(self.ptr, self.func, x.ptr, step_size, tol)
    def iterate(self):
        libgsl.gsl_multimin_fdfminimizer_iterate(self.ptr)
    def x(self):
        x = libgsl.gsl_multimin_fdfminimizer_x(self.ptr)
        return _vector_view_from_gsl(x)
    def minimum(self):
        return libgsl.gsl_multimin_fdfminimizer_minimum(self.ptr)
    def gradient(self):
        g = libgsl.gsl_multimin_fdfminimizer_gradient(self.ptr)
        return _vector_view_from_gsl(g)

    def test_gradient(self, epsabs):
        g  = libgsl.gsl_multimin_fdfminimizer_gradient(self.ptr)
        return libgsl.gsl_multimin_test_gradient(g, epsabs)
