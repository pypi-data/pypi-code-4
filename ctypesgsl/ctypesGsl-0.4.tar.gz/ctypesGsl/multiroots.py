"""Multidimensional root finding."""

from utils import *
from utils import _set_types, _add_function, _gsl_return_to_bool
from utils import _gsl_check_null_pointer, _gsl_check_status

from vector import gsl_vector, _vector_view_from_gsl, vector
from matrix import gsl_matrix, _matrix_view_from_gsl, matrix

# function to minimize

_GSL_MULTIROOT_F_TYPE   = CFUNCTYPE(c_int, POINTER(gsl_vector), py_object, POINTER(gsl_vector))
_GSL_MULTIROOT_DF_TYPE  = CFUNCTYPE(c_int, POINTER(gsl_vector), py_object, POINTER(gsl_matrix))
_GSL_MULTIROOT_FDF_TYPE = CFUNCTYPE(c_int, POINTER(gsl_vector), py_object, POINTER(gsl_vector), POINTER(gsl_matrix))

class gsl_multiroot_function(Structure):
    _fields_ = [("function", _GSL_MULTIROOT_F_TYPE),
                ("n", c_size_t),
                ("params", py_object)]
    def __init__(self, f, n, params = None):
        self._python_f = f
        self.n = n
        if params is None:
            ctypes_f = self._wrap_f_no_param
        else:
            ctypes_f = self._wrap_f
        Structure.__init__(self, _GSL_MULTIROOT_F_TYPE(ctypes_f), n, params)
    def _wrap_f(self, x, params, f):
        return self._python_f(_vector_view_from_gsl(x),
                              params,
                              _vector_view_from_gsl(f))
    def _wrap_f_no_param(self, x, params, f):
        return self._python_f(_vector_view_from_gsl(x),
                              _vector_view_from_gsl(f))
    def __call__(self, x):
        f = vector(self.n)
        self.function(x.ptr, self.params, f.ptr)
        return f



class gsl_multiroot_function_fdf(Structure):
    _fields_ = [("f",   _GSL_MULTIROOT_F_TYPE),
                ("df" , _GSL_MULTIROOT_DF_TYPE),
                ("fdf", _GSL_MULTIROOT_FDF_TYPE),
                ("n", c_size_t),
                ("params", py_object)]
    def __init__(self, f, df, fdf, n, params = None):
        """fdf can be None."""
        self._python_f = f
        self._python_df = df
        if fdf is None:
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
                           _GSL_MULTIROOT_F_TYPE(ctypes_f),
                           _GSL_MULTIROOT_DF_TYPE(ctypes_df),
                           _GSL_MULTIROOT_FDF_TYPE(ctypes_fdf),
                           n, params)
    def _wrap_f(self, x, _params, f):
        return self._python_f(_vector_view_from_gsl(x),
                              _params,
                              _vector_view_from_gsl(f))
    def _wrap_f_no_param(self, x, _params, f):
        return self._python_f(_vector_view_from_gsl(x),
                              _vector_view_from_gsl(f))
    def _wrap_df(self, x, _params, df):
        return self._python_df(_vector_view_from_gsl(x),
                               _params,
                               _matrix_view_from_gsl(df))
    def _wrap_df_no_param(self, x, _params, df):
        return self._python_df(_vector_view_from_gsl(x),
                               _matrix_view_from_gsl(df))
    def _wrap_fdf(self, x, _params, f, df):
        return self._python_fdf(_vector_view_from_gsl(x),
                                _params,
                                _vector_view_from_gsl(f),
                                _matrix_view_from_gsl(df))
    def _wrap_fdf_no_params(self, x, _params, f, df):
        return self._python_fdf(_vector_view_from_gsl(x),
                                _vector_view_from_gsl(f),
                                _matrix_view_from_gsl(df))

    def _default_fdf(self, x, _params, f, df):
        """compute fdf using f and df"""
        status1 = self._python_f(x, self.params, f)
        status2 = self._python_df(x, self.params, df)
        if status1 != GSL_SUCCESS:
            status = status1
        else:
            status = status2
        return status

    def eval_f(self, x):
        f = vector(self.n)
        self.f(x.ptr, self.params, f.ptr)
        return f
    def eval_df(self, x):
        df = matrix(self.n, self.n)
        self.df(x.ptr, self.params, df.ptr)
        return df
    def eval_fdf(self, x):
        f = vector(self.n)
        df = matrix(self.n, self.n)
        self.fdf(x.ptr, self.params, f.ptr, df.ptr)
        return f, df
    def __call__(self, x):
        return self.eval_fdf(x)



# types of root finders
class gsl_multiroot_fsolver_type(Structure):
    pass
_MULTIFSOLVER_TYPE_PTR = POINTER(gsl_multiroot_fsolver_type)
class gsl_multiroot_fdfsolver_type(Structure):
    pass
_MULTIFDFSOLVER_TYPE_PTR = POINTER(gsl_multiroot_fdfsolver_type)

multiroot_fdfsolver_hybridsj = _MULTIFDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fdfsolver_hybridsj")
multiroot_fdfsolver_hybridj  = _MULTIFDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fdfsolver_hybridj")
multiroot_fdfsolver_newton   = _MULTIFDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fdfsolver_newton")
multiroot_fdfsolver_gnewton  = _MULTIFDFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fdfsolver_gnewton")

multiroot_fsolver_hybrids    = _MULTIFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fsolver_hybrids")
multiroot_fsolver_hybrid     = _MULTIFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fsolver_hybrid")
multiroot_fsolver_dnewton    = _MULTIFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fsolver_dnewton")
multiroot_fsolver_broyden    = _MULTIFSOLVER_TYPE_PTR.in_dll(libgsl, "gsl_multiroot_fsolver_broyden")

# stopping condition tests
_add_function("multiroot_test_delta", _gsl_return_to_bool,
              [POINTER(gsl_vector), POINTER(gsl_vector),
               c_double, c_double], globals())
_add_function("multiroot_test_residual", _gsl_return_to_bool,
              [POINTER(gsl_vector), c_double], globals())


class gsl_multiroot_fsolver(Structure):
    pass
_set_types("multiroot_fsolver_alloc", POINTER(gsl_multiroot_fsolver), [_MULTIFSOLVER_TYPE_PTR])
_set_types("multiroot_fsolver_free", None, [POINTER(gsl_multiroot_fsolver)])
_set_types("multiroot_fsolver_set", _gsl_check_status,
           [POINTER(gsl_multiroot_fsolver),
            POINTER(gsl_multiroot_function),
            POINTER(gsl_vector)])
_set_types("multiroot_fsolver_iterate", _gsl_check_status, [POINTER(gsl_multiroot_fsolver)])
_set_types("multiroot_fsolver_root", POINTER(gsl_vector), [POINTER(gsl_multiroot_fsolver)])
_set_types("multiroot_fsolver_f", POINTER(gsl_vector), [POINTER(gsl_multiroot_fsolver)])
_set_types("multiroot_fsolver_dx", POINTER(gsl_vector), [POINTER(gsl_multiroot_fsolver)])


class multiroot_fsolver:
    def __init__(self, type, multi_func):
        self.libgsl = libgsl # helper for __del__
        self.func = multi_func
        self.ptr = libgsl.gsl_multiroot_fsolver_alloc(type, self.func.n)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_multiroot_fsolver_free(self.ptr)
    def init(self, x):
        """Set initial root."""
        libgsl.gsl_multiroot_fsolver_set(self.ptr, self.func, x.ptr)
    def iterate(self):
        libgsl.gsl_multiroot_fsolver_iterate(self.ptr)
    def root(self):
        r = libgsl.gsl_multiroot_fsolver_root(self.ptr)
        return _vector_view_from_gsl(r)
    def f(self):
        f = libgsl.gsl_multiroot_fsolver_f(self.ptr)
        return _vector_view_from_gsl(f)
    def dx(self):
        dx = libgsl.gsl_multiroot_fsolver_dx(self.ptr)
        return _vector_view_from_gsl(dx)

    def test_delta(self, epsabs, epsrel):
        dx = libgsl.gsl_multiroot_fsolver_dx(self.ptr)
        x  = libgsl.gsl_multiroot_fsolver_root(self.ptr)
        return libgsl.gsl_multiroot_test_delta(dx, x, epsabs, epsrel)
    def test_residual(self, epsabs):
        f  = libgsl.gsl_multiroot_fsolver_f(self.ptr)
        return libgsl.gsl_multiroot_test_residual(f, epsabs)


class gsl_multiroot_fdfsolver(Structure):
    pass
_set_types("multiroot_fdfsolver_alloc", POINTER(gsl_multiroot_fdfsolver), [_MULTIFDFSOLVER_TYPE_PTR])
_set_types("multiroot_fdfsolver_free", None, [POINTER(gsl_multiroot_fdfsolver)])
_set_types("multiroot_fdfsolver_set", _gsl_check_status,
           [POINTER(gsl_multiroot_fdfsolver),
            POINTER(gsl_multiroot_function_fdf),
            POINTER(gsl_vector)])
_set_types("multiroot_fdfsolver_iterate", _gsl_check_status, [POINTER(gsl_multiroot_fdfsolver)])
_set_types("multiroot_fdfsolver_root", POINTER(gsl_vector), [POINTER(gsl_multiroot_fdfsolver)])
_set_types("multiroot_fdfsolver_f", POINTER(gsl_vector), [POINTER(gsl_multiroot_fdfsolver)])
_set_types("multiroot_fdfsolver_dx", POINTER(gsl_vector), [POINTER(gsl_multiroot_fdfsolver)])

class multiroot_fdfsolver:
    def __init__(self, type, multi_fdffunc):
        self.libgsl = libgsl # helper for __del__
        self.func = multi_fdffunc
        self.ptr = libgsl.gsl_multiroot_fdfsolver_alloc(type, self.func.n)
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_multiroot_fdfsolver_free(self.ptr)
    def init(self, x):
        """Set initial root."""
        libgsl.gsl_multiroot_fdfsolver_set(self.ptr, self.func, x.ptr)
    def iterate(self):
        libgsl.gsl_multiroot_fdfsolver_iterate(self.ptr)
    def root(self):
        r = libgsl.gsl_multiroot_fdfsolver_root(self.ptr)
        return _vector_view_from_gsl(r)
    def f(self):
        f = libgsl.gsl_multiroot_fdfsolver_f(self.ptr)
        return _vector_view_from_gsl(f)
    def dx(self):
        dx = libgsl.gsl_multiroot_fdfsolver_dx(self.ptr)
        return _vector_view_from_gsl(dx)

    def test_delta(self, epsabs, epsrel):
        dx = libgsl.gsl_multiroot_fdfsolver_dx(self.ptr)
        x  = libgsl.gsl_multiroot_fdfsolver_root(self.ptr)
        return libgsl.gsl_multiroot_test_delta(dx, x, epsabs, epsrel)
    def test_residual(self, epsabs):
        f  = libgsl.gsl_multiroot_fdfsolver_f(self.ptr)
        return libgsl.gsl_multiroot_test_residual(f, epsabs)
