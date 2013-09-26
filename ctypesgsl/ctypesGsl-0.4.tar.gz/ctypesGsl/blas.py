
from ctypes import c_int
from ctypes import c_float, c_double
from cgsl_complex import gsl_complex, gsl_complex_float

from vector import vector, vector_float
from vector import gsl_vector, gsl_vector_float
from vector import vector_complex, vector_complex_float
from vector import gsl_vector_complex, gsl_vector_complex_float
from matrix import matrix, matrix_float
from matrix import gsl_matrix, gsl_matrix_float
from matrix import matrix_complex, matrix_complex_float
from matrix import gsl_matrix_complex, gsl_matrix_complex_float

from utils import *
from utils import _set_types
from utils import _gsl_check_status


# enumerated constants

#enum CBLAS_ORDER
CblasRowMajor = c_int(101)
CblasColMajor = c_int(102)
#enum CBLAS_TRANSPOSE
CblasNoTrans = c_int(111)
CblasTrans = c_int(112)
CblasConjTrans = c_int(113)
#enum CBLAS_UPLO
CblasUpper = c_int(121)
CblasLower = c_int(122)
#enum CBLAS_DIAG
CblasNonUnit = c_int(131)
CblasUnit = c_int(132)
#enum CBLAS_SIDE
CblasLeft = c_int(141)
CblasRight = c_int(142)

def _as_vector_float(v):
    if isinstance(v, vector_float):
        gsl_v = v
    else:
        gsl_v = vector_float(v)
    return gsl_v
def _as_vector(v):
    if isinstance(v, vector):
        gsl_v = v
    else:
        gsl_v = vector(v)
    return gsl_v
def _as_vector_complex(v):
    if isinstance(v, vector_complex):
        gsl_v = v
    else:
        gsl_v = vector_complex(v)
    return gsl_v
def _as_vector_complex_float(v):
    if isinstance(v, vector_complex_float):
        gsl_v = v
    else:
        gsl_v = vector_complex_float(v)
    return gsl_v

def _as_vector_float_dst(v):
    if isinstance(v, vector_float):
        gsl_v = v
    else:
        raise GSL_Error(GSL_EINVAL)
    return gsl_v
def _as_vector_dst(v):
    if isinstance(v, vector):
        gsl_v = v
    else:
        raise GSL_Error(GSL_EINVAL)
    return gsl_v
def _as_vector_complex_float_dst(v):
    if isinstance(v, vector_complex_float):
        gsl_v = v
    else:
        raise GSL_Error(GSL_EINVAL)
    return gsl_v
def _as_vector_complex_dst(v):
    if isinstance(v, vector_complex):
        gsl_v = v
    else:
        raise GSL_Error(GSL_EINVAL)
    return gsl_v

def _as_matrix_float(v):
    if isinstance(v, matrix_float):
        gsl_v = v
    else:
        gsl_v = matrix_float(v)
    return gsl_v
def _as_matrix(v):
    if isinstance(v, matrix):
        gsl_v = v
    else:
        gsl_v = matrix(v)
    return gsl_v
def _as_matrix_complex(v):
    if isinstance(v, matrix_complex):
        gsl_v = v
    else:
        gsl_v = matrix_complex(v)
    return gsl_v
def _as_matrix_complex_float(v):
    if isinstance(v, matrix_complex_float):
        gsl_v = v
    else:
        gsl_v = matrix_complex_float(v)
    return gsl_v

def _get_default_mat_shape_w_trans(A, TransA, B, TransB):
    if TransA == CblasNoTrans:
        s1 = A.shape[0]
    else:
        s1 = A.shape[1]
    if TransB == CblasNoTrans:
        s2 = B.shape[1]
    else:
        s2 = B.shape[0]
    return s1, s2
def _get_default_mat_shape_w_side(A, B, side):
    if side == CblasLeft:
        s1 = A.shape[0]
        s2 = B.shape[1]
    else:
        s1 = B.shape[0]
        s2 = A.shape[1]
    return s1, s2


_set_types("blas_sdsdot", _gsl_check_status, [c_float, POINTER(gsl_vector_float), POINTER(gsl_vector_float), POINTER(c_float)])
def blas_sdsdot(alpha, x, y):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    result = c_float()
    _res = libgsl.gsl_blas_sdsdot(alpha, _x_tmp.ptr, _y_tmp.ptr, byref(result))
    return result.value

_set_types("blas_sdot", _gsl_check_status, [POINTER(gsl_vector_float), POINTER(gsl_vector_float), POINTER(c_float)])
def blas_sdot(x, y):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    result = c_float()
    _res = libgsl.gsl_blas_sdot(_x_tmp.ptr, _y_tmp.ptr, byref(result))
    return result.value

_set_types("blas_dsdot", _gsl_check_status, [POINTER(gsl_vector_float), POINTER(gsl_vector_float), POINTER(c_double)])
def blas_dsdot(x, y):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    result = c_double()
    _res = libgsl.gsl_blas_dsdot(_x_tmp.ptr, _y_tmp.ptr, byref(result))
    return result.value

_set_types("blas_ddot", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), POINTER(c_double)])
def blas_ddot(x, y):
    _x_tmp = _as_vector(x)
    _y_tmp = _as_vector(y)
    result = c_double()
    _res = libgsl.gsl_blas_ddot(_x_tmp.ptr, _y_tmp.ptr, byref(result))
    return result.value

_set_types("blas_cdotu", _gsl_check_status, [POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float), POINTER(gsl_complex_float)])
def blas_cdotu(x, y):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    dotu = gsl_complex_float()
    _res = libgsl.gsl_blas_cdotu(_x_tmp.ptr, _y_tmp.ptr, byref(dotu))
    return dotu

_set_types("blas_zdotu", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_complex)])
def blas_zdotu(x, y):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    dotu = gsl_complex()
    _res = libgsl.gsl_blas_zdotu(_x_tmp.ptr, _y_tmp.ptr, byref(dotu))
    return dotu

_set_types("blas_cdotc", _gsl_check_status, [POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float), POINTER(gsl_complex_float)])
def blas_cdotc(x, y):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    dotc = gsl_complex_float()
    _res = libgsl.gsl_blas_cdotc(_x_tmp.ptr, _y_tmp.ptr, byref(dotc))
    return dotc

_set_types("blas_zdotc", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_complex)])
def blas_zdotc(x, y):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    dotc = gsl_complex()
    _res = libgsl.gsl_blas_zdotc(_x_tmp.ptr, _y_tmp.ptr, byref(dotc))
    return dotc

_set_types("blas_snrm2", c_float, [POINTER(gsl_vector_float)])
def blas_snrm2(x):
    _x_tmp = _as_vector_float(x)
    _res = libgsl.gsl_blas_snrm2(_x_tmp.ptr)
    return _res

_set_types("blas_dnrm2", c_double, [POINTER(gsl_vector)])
def blas_dnrm2(x):
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_blas_dnrm2(_x_tmp.ptr)
    return _res

_set_types("blas_scnrm2", c_float, [POINTER(gsl_vector_complex_float)])
def blas_scnrm2(x):
    _x_tmp = _as_vector_complex_float(x)
    _res = libgsl.gsl_blas_scnrm2(_x_tmp.ptr)
    return _res

_set_types("blas_dznrm2", c_double, [POINTER(gsl_vector_complex)])
def blas_dznrm2(x):
    _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_blas_dznrm2(_x_tmp.ptr)
    return _res

_set_types("blas_sasum", c_float, [POINTER(gsl_vector_float)])
def blas_sasum(x):
    _x_tmp = _as_vector_float(x)
    _res = libgsl.gsl_blas_sasum(_x_tmp.ptr)
    return _res

_set_types("blas_dasum", c_double, [POINTER(gsl_vector)])
def blas_dasum(x):
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_blas_dasum(_x_tmp.ptr)
    return _res

_set_types("blas_scasum", c_float, [POINTER(gsl_vector_complex_float)])
def blas_scasum(x):
    _x_tmp = _as_vector_complex_float(x)
    _res = libgsl.gsl_blas_scasum(_x_tmp.ptr)
    return _res

_set_types("blas_dzasum", c_double, [POINTER(gsl_vector_complex)])
def blas_dzasum(x):
    _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_blas_dzasum(_x_tmp.ptr)
    return _res

_set_types("blas_isamax", c_size_t, [POINTER(gsl_vector_float)])
def blas_isamax(x):
    _x_tmp = _as_vector_float(x)
    _res = libgsl.gsl_blas_isamax(_x_tmp.ptr)
    return _res

_set_types("blas_idamax", c_size_t, [POINTER(gsl_vector)])
def blas_idamax(x):
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_blas_idamax(_x_tmp.ptr)
    return _res

_set_types("blas_icamax", c_size_t, [POINTER(gsl_vector_complex_float)])
def blas_icamax(x):
    _x_tmp = _as_vector_complex_float(x)
    _res = libgsl.gsl_blas_icamax(_x_tmp.ptr)
    return _res

_set_types("blas_izamax", c_size_t, [POINTER(gsl_vector_complex)])
def blas_izamax(x):
    _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_blas_izamax(_x_tmp.ptr)
    return _res

_set_types("blas_sswap", _gsl_check_status, [POINTER(gsl_vector_float), POINTER(gsl_vector_float)])
def blas_sswap(x, y):
    _x_tmp = _as_vector_float_dst(x)
    _y_tmp = _as_vector_float_dst(y)
    _res = libgsl.gsl_blas_sswap(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_dswap", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector)])
def blas_dswap(x, y):
    _x_tmp = _as_vector_dst(x)
    _y_tmp = _as_vector_dst(y)
    _res = libgsl.gsl_blas_dswap(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_cswap", _gsl_check_status, [POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float)])
def blas_cswap(x, y):
    _x_tmp = _as_vector_complex_float_dst(x)
    _y_tmp = _as_vector_complex_float_dst(y)
    _res = libgsl.gsl_blas_cswap(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_zswap", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def blas_zswap(x, y):
    _x_tmp = _as_vector_complex_dst(x)
    _y_tmp = _as_vector_complex_dst(y)
    _res = libgsl.gsl_blas_zswap(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_scopy", _gsl_check_status, [POINTER(gsl_vector_float), POINTER(gsl_vector_float)])
def blas_scopy(x, y):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float_dst(y)
    _res = libgsl.gsl_blas_scopy(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_dcopy", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector)])
def blas_dcopy(x, y):
    _x_tmp = _as_vector(x)
    _y_tmp = _as_vector_dst(y)
    _res = libgsl.gsl_blas_dcopy(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_ccopy", _gsl_check_status, [POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float)])
def blas_ccopy(x, y):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float_dst(y)
    _res = libgsl.gsl_blas_ccopy(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_zcopy", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def blas_zcopy(x, y):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex_dst(y)
    _res = libgsl.gsl_blas_zcopy(_x_tmp.ptr, _y_tmp.ptr)
    return 

_set_types("blas_saxpy", _gsl_check_status, [c_float, POINTER(gsl_vector_float), POINTER(gsl_vector_float)])
def blas_saxpy(x, y, alpha=1):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    _res = libgsl.gsl_blas_saxpy(alpha, _x_tmp.ptr, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_daxpy", _gsl_check_status, [c_double, POINTER(gsl_vector), POINTER(gsl_vector)])
def blas_daxpy(x, y, alpha=1):
    _x_tmp = _as_vector(x)
    _y_tmp = _as_vector(y)
    _res = libgsl.gsl_blas_daxpy(alpha, _x_tmp.ptr, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_caxpy", _gsl_check_status, [gsl_complex_float, POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float)])
def blas_caxpy(x, y, alpha=1):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    _res = libgsl.gsl_blas_caxpy(alpha, _x_tmp.ptr, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_zaxpy", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def blas_zaxpy(x, y, alpha=1):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    _res = libgsl.gsl_blas_zaxpy(alpha, _x_tmp.ptr, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_sscal", None, [c_float, POINTER(gsl_vector_float)])
def blas_sscal(alpha, x):
    _x_tmp = _as_vector_float_dst(x)
    _res = libgsl.gsl_blas_sscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_dscal", None, [c_double, POINTER(gsl_vector)])
def blas_dscal(alpha, x):
    _x_tmp = _as_vector_dst(x)
    _res = libgsl.gsl_blas_dscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_cscal", None, [gsl_complex_float, POINTER(gsl_vector_complex_float)])
def blas_cscal(alpha, x):
    _x_tmp = _as_vector_complex_float_dst(x)
    _res = libgsl.gsl_blas_cscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_zscal", None, [gsl_complex, POINTER(gsl_vector_complex)])
def blas_zscal(alpha, x):
    _x_tmp = _as_vector_complex_dst(x)
    _res = libgsl.gsl_blas_zscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_csscal", None, [c_float, POINTER(gsl_vector_complex_float)])
def blas_csscal(alpha, x):
    _x_tmp = _as_vector_complex_float_dst(x)
    _res = libgsl.gsl_blas_csscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_zdscal", None, [c_double, POINTER(gsl_vector_complex)])
def blas_zdscal(alpha, x):
    _x_tmp = _as_vector_complex_dst(x)
    _res = libgsl.gsl_blas_zdscal(alpha, _x_tmp.ptr)
    return _res

_set_types("blas_srotg", _gsl_check_status, [POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)])
def blas_srotg(a, b):
    a = c_float(a)
    b = c_float(b)
    c = c_float()
    d = c_float()
    _res = libgsl.gsl_blas_srotg(a, b, byref(c), byref(d))
    return c.value, d.value

_set_types("blas_drotg", _gsl_check_status, [POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)])
def blas_drotg(a, b):
    a = c_double(a)
    b = c_double(b)
    c = c_double()
    d = c_double()
    _res = libgsl.gsl_blas_drotg(a, b, byref(c), byref(d))
    return c.value, d.value

_set_types("blas_srot", _gsl_check_status, [POINTER(gsl_vector_float), POINTER(gsl_vector_float), c_float, c_float])
def blas_srot(x, y, c, s):
    _x_tmp = _as_vector_float_dst(x)
    _y_tmp = _as_vector_float_dst(y)
    _res = libgsl.gsl_blas_srot(_x_tmp.ptr, _y_tmp.ptr, c, s)
    return 

_set_types("blas_drot", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), c_double, c_double])
def blas_drot(x, y, c, s):
    _x_tmp = _as_vector_dst(x)
    _y_tmp = _as_vector_dst(y)
    _res = libgsl.gsl_blas_drot(_x_tmp.ptr, _y_tmp.ptr, c, s)
    return 

_set_types("blas_sgemv", _gsl_check_status, [c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_vector_float), c_float, POINTER(gsl_vector_float)])
def blas_sgemv(A, x, TransA=CblasNoTrans, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_float(A)
    _x_tmp = _as_vector_float(x)
    if y is None:
        _y_tmp = vector_float(_A_tmp.shape[0])
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_float(y)
    _res = libgsl.gsl_blas_sgemv(TransA, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_dgemv", _gsl_check_status, [c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_vector), c_double, POINTER(gsl_vector)])
def blas_dgemv(A, x, TransA=CblasNoTrans, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix(A)
    _x_tmp = _as_vector(x)
    if y is None:
        _y_tmp = vector(_A_tmp.shape[0])
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector(y)
    _res = libgsl.gsl_blas_dgemv(TransA, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_cgemv", _gsl_check_status, [c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_vector_complex_float), gsl_complex_float, POINTER(gsl_vector_complex_float)])
def blas_cgemv(A, x, TransA=CblasNoTrans, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_complex_float(A)
    _x_tmp = _as_vector_complex_float(x)
    if y is None:
        _y_tmp = vector_complex_float(_A_tmp.shape[0])
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_complex_float(y)
    _res = libgsl.gsl_blas_cgemv(TransA, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_zgemv", _gsl_check_status, [c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex), gsl_complex, POINTER(gsl_vector_complex)])
def blas_zgemv(A, x, TransA=CblasNoTrans, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_complex(A)
    _x_tmp = _as_vector_complex(x)
    if y is None:
        _y_tmp = vector_complex(_A_tmp.shape[0])
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_complex(y)
    _res = libgsl.gsl_blas_zgemv(TransA, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_strmv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_float), POINTER(gsl_vector_float)])
def blas_strmv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_float(A)
    _x_tmp = _as_vector_float(x)
    _res = libgsl.gsl_blas_strmv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_dtrmv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix), POINTER(gsl_vector)])
def blas_dtrmv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix(A)
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_blas_dtrmv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_ctrmv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_complex_float), POINTER(gsl_vector_complex_float)])
def blas_ctrmv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_complex_float(A)
    _x_tmp = _as_vector_complex_float(x)
    _res = libgsl.gsl_blas_ctrmv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_ztrmv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex)])
def blas_ztrmv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_complex(A)
    _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_blas_ztrmv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_strsv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_float), POINTER(gsl_vector_float)])
def blas_strsv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_float(A)
    _x_tmp = _as_vector_float(x)
    _res = libgsl.gsl_blas_strsv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_dtrsv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix), POINTER(gsl_vector)])
def blas_dtrsv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix(A)
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_blas_dtrsv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_ctrsv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_complex_float), POINTER(gsl_vector_complex_float)])
def blas_ctrsv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_complex_float(A)
    _x_tmp = _as_vector_complex_float(x)
    _res = libgsl.gsl_blas_ctrsv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_ztrsv", _gsl_check_status, [c_int, c_int, c_int, POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex)])
def blas_ztrsv(A, x, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit):
    _A_tmp = _as_matrix_complex(A)
    _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_blas_ztrsv(Uplo, TransA, Diag, _A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("blas_ssymv", _gsl_check_status, [c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_vector_float), c_float, POINTER(gsl_vector_float)])
def blas_ssymv(A, x, Uplo=CblasUpper, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_float(A)
    _x_tmp = _as_vector_float(x)
    if y is None:
        _y_tmp = vector_float(_x_tmp.__len__())
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_float(y)
    _res = libgsl.gsl_blas_ssymv(Uplo, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_dsymv", _gsl_check_status, [c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_vector), c_double, POINTER(gsl_vector)])
def blas_dsymv(A, x, Uplo=CblasUpper, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix(A)
    _x_tmp = _as_vector(x)
    if y is None:
        _y_tmp = vector(_x_tmp.__len__())
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector(y)
    _res = libgsl.gsl_blas_dsymv(Uplo, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_chemv", _gsl_check_status, [c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_vector_complex_float), gsl_complex_float, POINTER(gsl_vector_complex_float)])
def blas_chemv(A, x, Uplo=CblasUpper, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_complex_float(A)
    _x_tmp = _as_vector_complex_float(x)
    if y is None:
        _y_tmp = vector_complex_float(_x_tmp.__len__())
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_complex_float(y)
    _res = libgsl.gsl_blas_chemv(Uplo, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_zhemv", _gsl_check_status, [c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex), gsl_complex, POINTER(gsl_vector_complex)])
def blas_zhemv(A, x, Uplo=CblasUpper, alpha=1, beta=1, y=None):
    _A_tmp = _as_matrix_complex(A)
    _x_tmp = _as_vector_complex(x)
    if y is None:
        _y_tmp = vector_complex(_x_tmp.__len__())
        _y_tmp.set_zero()
    else:
        _y_tmp = _as_vector_complex(y)
    _res = libgsl.gsl_blas_zhemv(Uplo, alpha, _A_tmp.ptr, _x_tmp.ptr, beta, _y_tmp.ptr)
    return _y_tmp

_set_types("blas_sger", _gsl_check_status, [c_float, POINTER(gsl_vector_float), POINTER(gsl_vector_float), POINTER(gsl_matrix_float)])
def blas_sger(x, y, A, alpha=1):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    _A_tmp = _as_matrix_float(A)
    _res = libgsl.gsl_blas_sger(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_dger", _gsl_check_status, [c_double, POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_matrix)])
def blas_dger(x, y, A, alpha=1):
    _x_tmp = _as_vector(x)
    _y_tmp = _as_vector(y)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_blas_dger(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_cgeru", _gsl_check_status, [gsl_complex_float, POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_cgeru(x, y, A, alpha=1):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    _A_tmp = _as_matrix_complex_float(A)
    _res = libgsl.gsl_blas_cgeru(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_zgeru", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def blas_zgeru(x, y, A, alpha=1):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_blas_zgeru(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_cgerc", _gsl_check_status, [gsl_complex_float, POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_cgerc(x, y, A, alpha=1):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    _A_tmp = _as_matrix_complex_float(A)
    _res = libgsl.gsl_blas_cgerc(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_zgerc", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def blas_zgerc(x, y, A, alpha=1):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_blas_zgerc(alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_ssyr", _gsl_check_status, [c_int, c_float, POINTER(gsl_vector_float), POINTER(gsl_matrix_float)])
def blas_ssyr(x, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_float(x)
    _A_tmp = _as_matrix_float(A)
    _res = libgsl.gsl_blas_ssyr(Uplo, alpha, _x_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_dsyr", _gsl_check_status, [c_int, c_double, POINTER(gsl_vector), POINTER(gsl_matrix)])
def blas_dsyr(x, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector(x)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_blas_dsyr(Uplo, alpha, _x_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_cher", _gsl_check_status, [c_int, c_float, POINTER(gsl_vector_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_cher(x, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_complex_float(x)
    _A_tmp = _as_matrix_complex_float(A)
    _res = libgsl.gsl_blas_cher(Uplo, alpha, _x_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_zher", _gsl_check_status, [c_int, c_double, POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def blas_zher(x, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_complex(x)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_blas_zher(Uplo, alpha, _x_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_ssyr2", _gsl_check_status, [c_int, c_float, POINTER(gsl_vector_float), POINTER(gsl_vector_float), POINTER(gsl_matrix_float)])
def blas_ssyr2(x, y, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_float(x)
    _y_tmp = _as_vector_float(y)
    _A_tmp = _as_matrix_float(A)
    _res = libgsl.gsl_blas_ssyr2(Uplo, alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_dsyr2", _gsl_check_status, [c_int, c_double, POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_matrix)])
def blas_dsyr2(x, y, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector(x)
    _y_tmp = _as_vector(y)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_blas_dsyr2(Uplo, alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_cher2", _gsl_check_status, [c_int, gsl_complex_float, POINTER(gsl_vector_complex_float), POINTER(gsl_vector_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_cher2(x, y, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_complex_float(x)
    _y_tmp = _as_vector_complex_float(y)
    _A_tmp = _as_matrix_complex_float(A)
    _res = libgsl.gsl_blas_cher2(Uplo, alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_zher2", _gsl_check_status, [c_int, gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def blas_zher2(x, y, A, Uplo=CblasUpper, alpha=1):
    _x_tmp = _as_vector_complex(x)
    _y_tmp = _as_vector_complex(y)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_blas_zher2(Uplo, alpha, _x_tmp.ptr, _y_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("blas_sgemm", _gsl_check_status, [c_int, c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_matrix_float), c_float, POINTER(gsl_matrix_float)])
def blas_sgemm(A, B, TransA=CblasNoTrans, TransB=CblasNoTrans, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_float(A)
    _B_tmp = _as_matrix_float(B)
    if C is None:
        _C_tmp = matrix_float(*_get_default_mat_shape_w_trans(_A_tmp, TransA, _B_tmp, TransB))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_float(C)
    _res = libgsl.gsl_blas_sgemm(TransA, TransB, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_dgemm", _gsl_check_status, [c_int, c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_matrix), c_double, POINTER(gsl_matrix)])
def blas_dgemm(A, B, TransA=CblasNoTrans, TransB=CblasNoTrans, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if C is None:
        _C_tmp = matrix(*_get_default_mat_shape_w_trans(_A_tmp, TransA, _B_tmp, TransB))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix(C)
    _res = libgsl.gsl_blas_dgemm(TransA, TransB, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_cgemm", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float), gsl_complex_float, POINTER(gsl_matrix_complex_float)])
def blas_cgemm(A, B, TransA=CblasNoTrans, TransB=CblasNoTrans, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    if C is None:
        _C_tmp = matrix_complex_float(*_get_default_mat_shape_w_trans(_A_tmp, TransA, _B_tmp, TransB))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_cgemm(TransA, TransB, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zgemm", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), gsl_complex, POINTER(gsl_matrix_complex)])
def blas_zgemm(A, B, TransA=CblasNoTrans, TransB=CblasNoTrans, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    if C is None:
        _C_tmp = matrix_complex(*_get_default_mat_shape_w_trans(_A_tmp, TransA, _B_tmp, TransB))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zgemm(TransA, TransB, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_ssymm", _gsl_check_status, [c_int, c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_matrix_float), c_float, POINTER(gsl_matrix_float)])
def blas_ssymm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_float(A)
    _B_tmp = _as_matrix_float(B)
    if C is None:
        _C_tmp = matrix_float(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_float(C)
    _res = libgsl.gsl_blas_ssymm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_dsymm", _gsl_check_status, [c_int, c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_matrix), c_double, POINTER(gsl_matrix)])
def blas_dsymm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if C is None:
        _C_tmp = matrix(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix(C)
    _res = libgsl.gsl_blas_dsymm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_csymm", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float), gsl_complex_float, POINTER(gsl_matrix_complex_float)])
def blas_csymm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    if C is None:
        _C_tmp = matrix_complex_float(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_csymm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zsymm", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), gsl_complex, POINTER(gsl_matrix_complex)])
def blas_zsymm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    if C is None:
        _C_tmp = matrix_complex(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zsymm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_chemm", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float), gsl_complex_float, POINTER(gsl_matrix_complex_float)])
def blas_chemm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    if C is None:
        _C_tmp = matrix_complex_float(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_chemm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zhemm", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), gsl_complex, POINTER(gsl_matrix_complex)])
def blas_zhemm(A, B, Side=CblasLeft, Uplo=CblasUpper, alpha=1, beta=1, C=None):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    if C is None:
        _C_tmp = matrix_complex(*_get_default_mat_shape_w_side(_A_tmp, _B_tmp, Side))
        _C_tmp.set_zero()
    else:
        _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zhemm(Side, Uplo, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_strmm", _gsl_check_status, [c_int, c_int, c_int, c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_matrix_float)])
def blas_strmm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_float(A)
    _B_tmp = _as_matrix_float(B)
    _res = libgsl.gsl_blas_strmm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_dtrmm", _gsl_check_status, [c_int, c_int, c_int, c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_matrix)])
def blas_dtrmm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    _res = libgsl.gsl_blas_dtrmm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_ctrmm", _gsl_check_status, [c_int, c_int, c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_ctrmm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    _res = libgsl.gsl_blas_ctrmm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_ztrmm", _gsl_check_status, [c_int, c_int, c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex)])
def blas_ztrmm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    _res = libgsl.gsl_blas_ztrmm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_strsm", _gsl_check_status, [c_int, c_int, c_int, c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_matrix_float)])
def blas_strsm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_float(A)
    _B_tmp = _as_matrix_float(B)
    _res = libgsl.gsl_blas_strsm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_dtrsm", _gsl_check_status, [c_int, c_int, c_int, c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_matrix)])
def blas_dtrsm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    _res = libgsl.gsl_blas_dtrsm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_ctrsm", _gsl_check_status, [c_int, c_int, c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float)])
def blas_ctrsm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    _res = libgsl.gsl_blas_ctrsm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_ztrsm", _gsl_check_status, [c_int, c_int, c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex)])
def blas_ztrsm(A, B, Side=CblasLeft, Uplo=CblasUpper, TransA=CblasNoTrans, Diag=CblasNonUnit, alpha=1):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    _res = libgsl.gsl_blas_ztrsm(Side, Uplo, TransA, Diag, alpha, _A_tmp.ptr, _B_tmp.ptr)
    return _B_tmp

_set_types("blas_ssyrk", _gsl_check_status, [c_int, c_int, c_float, POINTER(gsl_matrix_float), c_float, POINTER(gsl_matrix_float)])
def blas_ssyrk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_float(A)
    _C_tmp = _as_matrix_float(C)
    _res = libgsl.gsl_blas_ssyrk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_dsyrk", _gsl_check_status, [c_int, c_int, c_double, POINTER(gsl_matrix), c_double, POINTER(gsl_matrix)])
def blas_dsyrk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix(A)
    _C_tmp = _as_matrix(C)
    _res = libgsl.gsl_blas_dsyrk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_csyrk", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), gsl_complex_float, POINTER(gsl_matrix_complex_float)])
def blas_csyrk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex_float(A)
    _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_csyrk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zsyrk", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), gsl_complex, POINTER(gsl_matrix_complex)])
def blas_zsyrk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex(A)
    _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zsyrk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_cherk", _gsl_check_status, [c_int, c_int, c_float, POINTER(gsl_matrix_complex_float), c_float, POINTER(gsl_matrix_complex_float)])
def blas_cherk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex_float(A)
    _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_cherk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zherk", _gsl_check_status, [c_int, c_int, c_double, POINTER(gsl_matrix_complex), c_double, POINTER(gsl_matrix_complex)])
def blas_zherk(A, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex(A)
    _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zherk(Uplo, Trans, alpha, _A_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_ssyr2k", _gsl_check_status, [c_int, c_int, c_float, POINTER(gsl_matrix_float), POINTER(gsl_matrix_float), c_float, POINTER(gsl_matrix_float)])
def blas_ssyr2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_float(A)
    _B_tmp = _as_matrix_float(B)
    _C_tmp = _as_matrix_float(C)
    _res = libgsl.gsl_blas_ssyr2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_dsyr2k", _gsl_check_status, [c_int, c_int, c_double, POINTER(gsl_matrix), POINTER(gsl_matrix), c_double, POINTER(gsl_matrix)])
def blas_dsyr2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    _C_tmp = _as_matrix(C)
    _res = libgsl.gsl_blas_dsyr2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_csyr2k", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float), gsl_complex_float, POINTER(gsl_matrix_complex_float)])
def blas_csyr2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_csyr2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zsyr2k", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), gsl_complex, POINTER(gsl_matrix_complex)])
def blas_zsyr2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zsyr2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_cher2k", _gsl_check_status, [c_int, c_int, gsl_complex_float, POINTER(gsl_matrix_complex_float), POINTER(gsl_matrix_complex_float), c_float, POINTER(gsl_matrix_complex_float)])
def blas_cher2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex_float(A)
    _B_tmp = _as_matrix_complex_float(B)
    _C_tmp = _as_matrix_complex_float(C)
    _res = libgsl.gsl_blas_cher2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

_set_types("blas_zher2k", _gsl_check_status, [c_int, c_int, gsl_complex, POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), c_double, POINTER(gsl_matrix_complex)])
def blas_zher2k(A, B, C, Uplo=CblasUpper, Trans=CblasNoTrans, alpha=1, beta=1):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    _C_tmp = _as_matrix_complex(C)
    _res = libgsl.gsl_blas_zher2k(Uplo, Trans, alpha, _A_tmp.ptr, _B_tmp.ptr, beta, _C_tmp.ptr)
    return _C_tmp

