"""Basic functionality and utilities for ctypesGsl package"""

from new import instancemethod

from ctypes import CDLL, RTLD_GLOBAL, POINTER, byref, pointer
from ctypes import Structure, CFUNCTYPE, cast
from ctypes import c_char, c_int, c_uint, c_long, c_ulong, c_short, c_ushort
from ctypes import c_float, c_double
from ctypes import c_size_t, c_void_p, c_char_p, py_object
from ctypes.util import find_library


try:
    from functools import partial
except:
    class partial(object):
        def __init__(*args, **kw):
            self = args[0]
            self.fn, self.args, self.kw = (args[1], args[2:], kw)
        def __call__(self, *args, **kw):
            if kw and self.kw:
                d = self.kw.copy()
                d.update(kw)
            else:
                d = kw or self.kw
            return self.fn(*(self.args + args), **d)


def _set_types(fname, restype, argtypes):
    f = libgsl.__getattr__("gsl_" + fname)
    f.restype = restype
    f.argtypes = argtypes
    return f
def _add_function(fname, restype, argtypes, globs = globals()):
    new_m = _set_types(fname, restype, argtypes)
    globs[fname] = new_m

def _new_method(func, self, *args, **kwargs):
    """Helper for dynamically adding methods to classes."""
    return func(self.ptr, *args, **kwargs)
def _add_method(cls, fname, restype, argtypes, class_ptr_type = c_void_p, method_name = None):
    """Dynamically add gsl method to a class.

    Useful for methods which do not require speed."""
    new_m = _set_types(fname, restype, [class_ptr_type] + argtypes)
    method = instancemethod(partial(_new_method, new_m), None, cls)
    if method_name is None:
        method_name = fname[fname.rindex('_') + 1:]
    setattr(cls, method_name, method)



# load the libraries
def __load_lib(libname, mode = None):
    lib_path = find_library(libname)
    if lib_path is None:
        raise RuntimeError("Could not find the " + libname + " library")
    if mode is None:
        lib = CDLL(lib_path)
    else:
        lib = CDLL(lib_path, mode)
    return lib

libc = __load_lib("c")
libblas = __load_lib("blas", mode = RTLD_GLOBAL)
libgsl = __load_lib("gsl")


### RETURN CODES
GSL_SUCCESS = 0
GSL_FAILURE  = -1
GSL_CONTINUE = -2  # iteration has not converged
GSL_EDOM     = 1   # input domain error, e.g sqrt(-1)
GSL_ERANGE   = 2   # output range error, e.g. exp(1e100)
GSL_EFAULT   = 3   # invalid pointer
GSL_EINVAL   = 4   # invalid argument supplied by user
GSL_EFAILED  = 5   # generic failure
GSL_EFACTOR  = 6   # factorization failed
GSL_ESANITY  = 7   # sanity check failed - shouldn't happen
GSL_ENOMEM   = 8   # malloc failed
GSL_EBADFUNC = 9   # problem with user-supplied function
GSL_ERUNAWAY = 10  # iterative process is out of control
GSL_EMAXITER = 11  # exceeded max number of iterations
GSL_EZERODIV = 12  # tried to divide by zero
GSL_EBADTOL  = 13  # user specified an invalid tolerance
GSL_ETOL     = 14  # failed to reach the specified tolerance
GSL_EUNDRFLW = 15  # underflow
GSL_EOVRFLW  = 16  # overflow 
GSL_ELOSS    = 17  # loss of accuracy
GSL_EROUND   = 18  # failed because of roundoff error
GSL_EBADLEN  = 19  # matrix, vector lengths are not conformant
GSL_ENOTSQR  = 20  # matrix not square
GSL_ESING    = 21  # apparent singularity detected
GSL_EDIVERGE = 22  # integral or series is divergent
GSL_EUNSUP   = 23  # requested feature is not supported by the hardware
GSL_EUNIMPL  = 24  # requested feature not (yet) implemented
GSL_ECACHE   = 25  # cache limit exceeded
GSL_ETABLE   = 26  # table limit exceeded
GSL_ENOPROG  = 27  # iteration is not making progress towards solution
GSL_ENOPROGJ = 28  # jacobian evaluations are not improving the solution
GSL_ETOLF    = 29  # cannot reach the specified tolerance in F
GSL_ETOLX    = 30  # cannot reach the specified tolerance in X
GSL_ETOLG    = 31  # cannot reach the specified tolerance in gradient
GSL_EOF      = 32  # end of file

def _int_to_bool(i):
    return bool(i)
def _gsl_return_to_bool(i):
    """Convert GSL return value to Bool.

    No exceptions are raised.  True return value means successful
    execution (the meaning depends on specific function)."""
    return i == GSL_SUCCESS
        

### ERROR HANDLING

_add_function("strerror", c_char_p, [c_int])

class GSL_Error(RuntimeError):
    def __init__(self, gsl_err_code, fl = None, line = None, reason = None, result = None):
        msg = "gsl: "
        if fl is not None:
            msg += fl+":"
        if line is not None:
            msg += str(line)+":"
        if msg[-1] != " ":
            msg += " "
        msg += "ERROR: "
        if reason is not None:
            msg += reason
        else:
            msg += strerror(gsl_err_code)
        RuntimeError.__init__(self, msg)
        self.gsl_err_code = gsl_err_code
        self.fl = fl # file in which error occurred
        self.line = line
        self.reason = reason
        self.result = result # result to be returned by the function

# helper function to test allocation
def _gsl_check_null_pointer(p):
    """Raises an exception if a allocation failed in a GSL function."""
    p = cast(p, c_void_p)
    if p == 0:
        raise GSL_Error(GSL_ENOMEM)
    return p

### ctypesGsl error handling
# handling of gsl status returned by functions
def _ctypesGsl_status_exception(status_code, result):
    raise GSL_Error(status_code, result = result)
def _ctypesGsl_status_warning(status_code, result):
    print "WARNING: " + str(GSL_Error(status_code, result = result))
    return status_code
def _ctypesGsl_status_off(status_code, result):
    return status_code

# current status handler function
ctypesGsl_status_handler = _ctypesGsl_status_exception

def set_status_handler(h):
    global ctypesGsl_status_handler
    old_handler = ctypesGsl_status_handler
    ctypesGsl_status_handler = h
    return old_handler
def set_status_handler_off():
    return set_status_handler(_ctypesGsl_status_off)
def set_status_handler_warning():
    return set_status_handler(_ctypesGsl_status_warning)
def set_status_handler_exception():
    return set_status_handler(_ctypesGsl_status_exception)

# method for testing return values
def _gsl_check_status(status_code, result = None):
    """Raises an exception if a GSL function returns an error
    condition."""
    if status_code != GSL_SUCCESS:
        ctypesGsl_status_handler(status_code, result)
    return status_code

### internal gsl error handling
GSL_ERROR_HANDLER_T = CFUNCTYPE(None, c_char_p, c_char_p, c_int, c_int)
_add_function("set_error_handler", GSL_ERROR_HANDLER_T, [GSL_ERROR_HANDLER_T])
_add_function("set_error_handler_off", GSL_ERROR_HANDLER_T, [])

# create our own error handler to raise exceptions instead of aborts
def __ctypesGsl_error_handler_warning(reason, fl, line, gsl_errno):
    print "WARNING: " + str(GSL_Error(gsl_errno, fl, line, reason))
    # !!! currently, due to limitations in ctypes, this exception is
    # !!! not thrown to the program, just printed
    # raise GSL_Error(gsl_errno, fl, line, reason)
def __ctypesGsl_error_handler_exception(reason, fl, line, gsl_errno):
    # !!! currently, due to limitations in ctypes, this exception is
    # !!! not thrown to the program, just printed
    raise GSL_Error(gsl_errno, fl, line, reason)
_ctypesGsl_error_handler_warning   = GSL_ERROR_HANDLER_T(__ctypesGsl_error_handler_warning)
_ctypesGsl_error_handler_exception = GSL_ERROR_HANDLER_T(__ctypesGsl_error_handler_exception)

def set_error_handler_warning():
    return set_error_handler(_ctypesGsl_error_handler_warning)
def set_error_handler_exception():
    return set_error_handler(_ctypesGsl_error_handler_exception)

# set the default handler
gsl_default_error_handler = set_error_handler_warning()



### gsl_function and such

_GSL_FUNC_TYPE = CFUNCTYPE(c_double, c_double, py_object)

class gsl_function(Structure):
    _fields_ = [("function", CFUNCTYPE(c_double, c_double, py_object)),
                ("params", py_object)]
    def __init__(self, function, params = None):
        if params is None:
            self._python_function = function
            function = self._no_param_wrapper
        Structure.__init__(self, CFUNCTYPE(c_double, c_double, py_object)(function), params)
    def _no_param_wrapper(self, x, params):
        return self._python_function(x)
    def __call__(self, x):
        return self.function(x, self.params)

def GSL_FN_EVAL(f, x):
    return f(x)


class gsl_function_fdf(Structure):
    _fields_ = [("f"  , CFUNCTYPE(c_double, c_double, py_object)),
                ("df" , CFUNCTYPE(c_double, c_double, py_object)),
                ("fdf", CFUNCTYPE(None, c_double, py_object, POINTER(c_double), POINTER(c_double))),
                ("params", py_object)]
    def __init__(self, f, df, fdf = None, params = None):
        if fdf is None:
            ctypes_fdf = self._default_fdf
        else:
            self._python_fdf = fdf
            ctypes_fdf = self._wrap_fdf
        Structure.__init__(self,
                           CFUNCTYPE(c_double, c_double, py_object)(f),
                           CFUNCTYPE(c_double, c_double, py_object)(df),
                           CFUNCTYPE(None, c_double, py_object, POINTER(c_double), POINTER(c_double))(ctypes_fdf),
                           params)
    def _wrap_fdf(self, x, _params, f_out, df_out):
        """wrap a python (returning a pair) fdf function"""
        f_out.contents.value, df_out.contents.value = self._python_fdf(x, self.params)
    def _default_fdf(self, x, _params, f_out, df_out):
        """compute fdf using f and df"""
        f_out.contents.value  = self.f(x, self.params)
        df_out.contents.value = self.df(x, self.params)
    def __call__(self, x):
        f_out  = c_double()
        df_out = c_double()
        self.fdf(x, self.params, byref(f_out), byref(df_out))
        return f_out.value, df_out.value



