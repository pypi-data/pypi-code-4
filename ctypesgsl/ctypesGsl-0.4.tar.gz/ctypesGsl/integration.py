"""Integration"""

from utils import *
from utils import _set_types, _gsl_return_to_bool, _add_function
from utils import _gsl_check_status, _gsl_check_null_pointer

from basic import M_PI


_set_types("integration_qng", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double, c_double,
            POINTER(c_double), POINTER(c_double), POINTER(c_size_t)])

def integration_qng(gsl_function, a, b, epsabs, epsrel = 0.0):
    result = c_double()
    abserr = c_double()
    neval  = c_size_t()
    status = libgsl.gsl_integration_qng(gsl_function, a, b, epsabs, epsrel,
                               byref(result), byref(abserr), byref(neval))
    res = (result.value, abserr.value, neval.value)
    _gsl_check_status(status, result = res)
    return res

#### INTEGRATION WORKSPACE
class gsl_integration_workspace(Structure):
    pass

_set_types("integration_workspace_alloc", POINTER(gsl_integration_workspace), [c_size_t])
_set_types("integration_workspace_free",  None, [POINTER(gsl_integration_workspace)])

class integration_workspace:
    def __init__(self, n = 1000):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_integration_workspace_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_integration_workspace_free(self.ptr)


def _ensure_workspace(workspace, workspace_size, limit):
    """Allocate workspace if necessary."""
    if workspace is None:
        workspace = integration_workspace(workspace_size)
    if limit is None:
        limit = workspace.size
    return workspace, limit

GSL_INTEG_GAUSS15 = 1  # 15 point Gauss-Kronrod rule
GSL_INTEG_GAUSS21 = 2  # 21 point Gauss-Kronrod rule
GSL_INTEG_GAUSS31 = 3  # 31 point Gauss-Kronrod rule
GSL_INTEG_GAUSS41 = 4  # 41 point Gauss-Kronrod rule
GSL_INTEG_GAUSS51 = 5  # 51 point Gauss-Kronrod rule
GSL_INTEG_GAUSS61 = 6  # 61 point Gauss-Kronrod rule

_set_types("integration_qag", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double, c_double,
            c_size_t, c_int, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qag(gsl_function, a, b, epsabs, epsrel = 0.0, workspace = None,
                key = GSL_INTEG_GAUSS21,
                workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qag(gsl_function, a, b, epsabs, epsrel,
                                        limit, key, workspace.ptr,
                                        byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res


_set_types("integration_qags", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qags(gsl_function, a, b, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qags(gsl_function, a, b, epsabs, epsrel,
                                        limit, workspace.ptr,
                                        byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

_set_types("integration_qagp", c_int,
           [POINTER(gsl_function), POINTER(c_double), c_size_t, c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qagp(gsl_function, pts, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    npts = len(pts)
    c_pts = (c_double * npts)(*pts)
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qagp(gsl_function, c_pts, npts,
                                         epsabs, epsrel,
                                         limit, workspace.ptr,
                                         byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

_set_types("integration_qagi", c_int,
           [POINTER(gsl_function), c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])
_set_types("integration_qagiu", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])
_set_types("integration_qagil", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qagi(gsl_function, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qagi(gsl_function, epsabs, epsrel,
                                         limit, workspace.ptr,
                                         byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res
def integration_qagiu(gsl_function, a, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qagiu(gsl_function, a, epsabs, epsrel,
                                          limit, workspace.ptr,
                                          byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res
def integration_qagil(gsl_function, b, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qagil(gsl_function, b, epsabs, epsrel,
                                          limit, workspace.ptr,
                                          byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res


#### Weighted integration


# Cauchy principal values
_set_types("integration_qawc", c_int,
           [POINTER(gsl_function), c_double, c_double, c_double, c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qawc(gsl_function, a, b, c, epsabs, epsrel = 0.0, workspace = None,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    status = libgsl.gsl_integration_qawc(gsl_function, a, b, c, epsabs, epsrel,
                                        limit, workspace.ptr,
                                        byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

# singular weight table
class gsl_integration_qaws_table(Structure):
    pass

_set_types("integration_qaws_table_alloc",
           POINTER(gsl_integration_qaws_table),
           [c_double, c_double, c_int, c_int])
_set_types("integration_qaws_table_free",
           None,
           [POINTER(gsl_integration_qaws_table)])
_set_types("integration_qaws_table_set",
           _gsl_check_status,
           [POINTER(gsl_integration_qaws_table), c_double, c_double, c_int, c_int])

class integration_qaws_table:
    def __init__(self, alpha, beta, mu, nu):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_integration_qaws_table_alloc(alpha, beta, mu, nu)
        _gsl_check_null_pointer(self.ptr)
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.nu = nu
    def set(self, alpha, beta, mu, nu):
        libgsl.gsl_integration_qaws_table_set(self.ptr, alpha, beta, mu, nu)
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.nu = nu
    def __del__(self):
        self.libgsl.gsl_integration_qaws_table_free(self.ptr)

_set_types("integration_qaws", c_int,
           [POINTER(gsl_function), c_double, c_double,
            POINTER(gsl_integration_qaws_table),
            c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(c_double), POINTER(c_double)])

def integration_qaws(gsl_function, a, b, epsabs, epsrel = 0.0,
                     qaws_table = None,
                     workspace = None,
                     alpha = 0, beta = 0, mu = 0, nu = 0,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    if qaws_table is None:
        qaws_table = integration_qaws_table(alpha, beta, mu, nu)
    status = libgsl.gsl_integration_qaws(gsl_function, a, b, qaws_table.ptr,
                                         epsabs, epsrel,
                                         limit, workspace.ptr,
                                         byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

# oscillatory functions

GSL_INTEG_COSINE = 0
GSL_INTEG_SINE   = 1

# oscillatory weight table
class gsl_integration_qawo_table(Structure):
    pass

_set_types("integration_qawo_table_alloc",
           POINTER(gsl_integration_qawo_table),
           [c_double, c_double, c_int, c_size_t])
_set_types("integration_qawo_table_free",
           None,
           [POINTER(gsl_integration_qawo_table)])
_set_types("integration_qawo_table_set",
           _gsl_check_status,
           [POINTER(gsl_integration_qawo_table), c_double, c_double, c_int])
_set_types("integration_qawo_table_set_length",
           _gsl_check_status,
           [POINTER(gsl_integration_qawo_table), c_double])

class integration_qawo_table:
    def __init__(self, omega, L, is_sine = GSL_INTEG_COSINE, n = 10):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_integration_qawo_table_alloc(omega, L, is_sine, n)
        _gsl_check_null_pointer(self.ptr)
        self.omega = omega
        self.L = L
        self.is_sine = is_sine
        self.n = n
    def set(self, omega, L, is_sine = GSL_INTEG_COSINE, n = 10):
        libgsl.gsl_integration_qawo_table_set(self.ptr, omega, L, is_sine, n)
        self.omega = omega
        self.L = L
        self.is_sine = is_sine
        self.n = n
    def set_length(self, L):
        libgsl.gsl_integration_qawo_table_set_length(self.ptr, L)
        self.L = L
    def __del__(self):
        self.libgsl.gsl_integration_qawo_table_free(self.ptr)


_set_types("integration_qawo", c_int,
           [POINTER(gsl_function), c_double,
            c_double, c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(gsl_integration_qawo_table),
            POINTER(c_double), POINTER(c_double)])

def integration_qawo(gsl_function, a, epsabs, epsrel = 0.0,
                     qawo_table = None,
                     workspace = None,
                     omega = 2 * M_PI, L = 1, is_sine = GSL_INTEG_COSINE, n = 10,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, limit = _ensure_workspace(workspace, workspace_size, limit)
    if qawo_table is None:
        qawo_table = integration_qawo_table(omega, L, is_sine, n)
    status = libgsl.gsl_integration_qawo(gsl_function, a,
                                         epsabs, epsrel,
                                         limit, workspace.ptr,
                                         qawo_table.ptr,
                                         byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res

# Fourier integrals
_set_types("integration_qawf", c_int,
           [POINTER(gsl_function), c_double,
            c_double,
            c_size_t, POINTER(gsl_integration_workspace),
            POINTER(gsl_integration_workspace),
            POINTER(gsl_integration_qawo_table),
            POINTER(c_double), POINTER(c_double)])

def integration_qawf(gsl_function, a, epsabs,
                     qawo_table = None,
                     workspace = None,
                     cycle_workspace = None,
                     omega = 2 * M_PI, is_sine = GSL_INTEG_COSINE, n = 10,
                     workspace_size = 1000, limit = None):
    result = c_double()
    abserr = c_double()
    workspace, work_limit = _ensure_workspace(workspace, workspace_size, limit)
    cycle_workspace, cycle_limit = _ensure_workspace(cycle_workspace, workspace_size, limit)
    limit = min(work_limit, cycle_limit)
    if qawo_table is None:
        qawo_table = integration_qawo_table(omega, 1, is_sine, n) # L is unused
    status = libgsl.gsl_integration_qawf(gsl_function, a, epsabs,
                                         limit, workspace.ptr, cycle_workspace.ptr,
                                         qawo_table.ptr,
                                         byref(result), byref(abserr))
    res = (result.value, abserr.value)
    _gsl_check_status(status, result = res)
    return res
