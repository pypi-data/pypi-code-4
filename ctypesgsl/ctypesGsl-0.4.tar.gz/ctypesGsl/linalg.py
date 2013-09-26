
from ctypes import c_int, c_double

from cgsl_complex import gsl_complex

from utils import *
from utils import _set_types
from utils import _gsl_check_status

from vector import vector, gsl_vector
from vector import vector_complex, gsl_vector_complex
from matrix import matrix, gsl_matrix
from matrix import matrix_complex, gsl_matrix_complex

from blas import _as_vector, _as_vector_dst
from blas import _as_vector_complex, _as_vector_complex_dst
from blas import _as_matrix, _as_matrix_complex

from permutation import gsl_permutation, permutation

def _as_perm_dst(p, default_size):
    if p is None:
        p = permutation(default_size)
        pptr = p.ptr
    else:
        if isinstance(p, gsl_permutation):
            pptr = p
        elif isinstance(p, permutation):
            pptr = p.ptr
        else:
            raise GSL_Error(GSL_EINVAL, "Not a permutation")
    return p, pptr

_set_types("linalg_LU_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(c_int)])
def linalg_LU_decomp(A, p=None):
    _A_tmp = _as_matrix(A)
    p, pptr = _as_perm_dst(p, _A_tmp.shape[1])
    signum = c_int()
    _res = libgsl.gsl_linalg_LU_decomp(_A_tmp.ptr, pptr, byref(signum))
    return _A_tmp, p, signum.value

_set_types("linalg_complex_LU_decomp", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_permutation), POINTER(c_int)])
def linalg_complex_LU_decomp(A, p=None):
    _A_tmp = _as_matrix_complex(A)
    p, pptr = _as_perm_dst(p, _A_tmp.shape[1])
    signum = c_int()
    _res = libgsl.gsl_linalg_complex_LU_decomp(_A_tmp.ptr, pptr, byref(signum))
    return _A_tmp, p, signum.value

_set_types("linalg_LU_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_LU_solve(LU, p, b, x=None):
    _LU_tmp = _as_matrix(LU)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_LU_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_LU_solve(_LU_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_complex_LU_solve", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_permutation), POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def linalg_complex_LU_solve(LU, p, b, x=None):
    _LU_tmp = _as_matrix_complex(LU)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector_complex(b)
    if x is None:
        _x_tmp = vector_complex(_LU_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_linalg_complex_LU_solve(_LU_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_LU_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector)])
def linalg_LU_svx(LU, p, x):
    _LU_tmp = _as_matrix(LU)
    if isinstance(p, permutation):
        p = p.ptr
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_LU_svx(_LU_tmp.ptr, p, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_complex_LU_svx", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_permutation), POINTER(gsl_vector_complex)])
def linalg_complex_LU_svx(LU, p, x=None):
    _LU_tmp = _as_matrix_complex(LU)
    if isinstance(p, permutation):
        p = p.ptr
    if x is None:
        _x_tmp = vector_complex(_LU_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_linalg_complex_LU_svx(_LU_tmp.ptr, p, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_LU_refine", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_LU_refine(A, LU, p, b, x, residual=None):
    _A_tmp = _as_matrix(A)
    _LU_tmp = _as_matrix(LU)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector(b)
    _x_tmp = _as_vector(x)
    if residual is None:
        _residual_tmp = vector(_A_tmp.shape[1])
        _residual_tmp.set_zero()
    else:
        _residual_tmp = _as_vector(residual)
    _res = libgsl.gsl_linalg_LU_refine(_A_tmp.ptr, _LU_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr, _residual_tmp.ptr)
    return _x_tmp, _residual_tmp

_set_types("linalg_complex_LU_refine", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), POINTER(gsl_permutation), POINTER(gsl_vector_complex), POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def linalg_complex_LU_refine(A, LU, p, b, x, residual=None):
    _A_tmp = _as_matrix_complex(A)
    _LU_tmp = _as_matrix_complex(LU)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector_complex(b)
    _x_tmp = _as_vector_complex(x)
    if residual is None:
        _residual_tmp = vector_complex(_A_tmp.shape[1])
        _residual_tmp.set_zero()
    else:
        _residual_tmp = _as_vector_complex(residual)
    _res = libgsl.gsl_linalg_complex_LU_refine(_A_tmp.ptr, _LU_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr, _residual_tmp.ptr)
    return _x_tmp, _residual_tmp

_set_types("linalg_LU_invert", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_matrix)])
def linalg_LU_invert(LU, p, inverse=None):
    _LU_tmp = _as_matrix(LU)
    if isinstance(p, permutation):
        p = p.ptr
    if inverse is None:
        _inverse_tmp = matrix(*_LU_tmp.shape)
        _inverse_tmp.set_zero()
    else:
        _inverse_tmp = _as_matrix(inverse)
    _res = libgsl.gsl_linalg_LU_invert(_LU_tmp.ptr, p, _inverse_tmp.ptr)
    return _inverse_tmp

_set_types("linalg_complex_LU_invert", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_permutation), POINTER(gsl_matrix_complex)])
def linalg_complex_LU_invert(LU, p, inverse=None):
    _LU_tmp = _as_matrix_complex(LU)
    if isinstance(p, permutation):
        p = p.ptr
    if inverse is None:
        _inverse_tmp = matrix_complex(*_LU_tmp.shape)
        _inverse_tmp.set_zero()
    else:
        _inverse_tmp = _as_matrix_complex(inverse)
    _res = libgsl.gsl_linalg_complex_LU_invert(_LU_tmp.ptr, p, _inverse_tmp.ptr)
    return _inverse_tmp

_set_types("linalg_LU_det", c_double, [POINTER(gsl_matrix), c_int])
def linalg_LU_det(LU, signum):
    _LU_tmp = _as_matrix(LU)
    _res = libgsl.gsl_linalg_LU_det(_LU_tmp.ptr, signum)
    return _res

_set_types("linalg_complex_LU_det", gsl_complex, [POINTER(gsl_matrix_complex), c_int])
def linalg_complex_LU_det(LU, signum):
    _LU_tmp = _as_matrix_complex(LU)
    _res = libgsl.gsl_linalg_complex_LU_det(_LU_tmp.ptr, signum)
    return _res

_set_types("linalg_LU_lndet", c_double, [POINTER(gsl_matrix)])
def linalg_LU_lndet(LU):
    _LU_tmp = _as_matrix(LU)
    _res = libgsl.gsl_linalg_LU_lndet(_LU_tmp.ptr)
    return _res

_set_types("linalg_LU_sgndet", c_int, [POINTER(gsl_matrix), c_int])
def linalg_LU_sgndet(LU, signum):
    _LU_tmp = _as_matrix(LU)
    _res = libgsl.gsl_linalg_LU_sgndet(_LU_tmp.ptr, signum)
    return _res

_set_types("linalg_complex_LU_lndet", c_double, [POINTER(gsl_matrix_complex)])
def linalg_complex_LU_lndet(LU):
    _LU_tmp = _as_matrix_complex(LU)
    _res = libgsl.gsl_linalg_complex_LU_lndet(_LU_tmp.ptr)
    return _res

_set_types("linalg_complex_LU_sgndet", gsl_complex, [POINTER(gsl_matrix_complex), c_int])
def linalg_complex_LU_sgndet(LU, signum):
    _LU_tmp = _as_matrix_complex(LU)
    _res = libgsl.gsl_linalg_complex_LU_sgndet(_LU_tmp.ptr, signum)
    return _res

_set_types("linalg_QR_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_QR_decomp(A, tau=None):
    _A_tmp = _as_matrix(A)
    if tau is None:
        _tau_tmp = vector(min(*_A_tmp.shape))
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector(tau)
    _res = libgsl.gsl_linalg_QR_decomp(_A_tmp.ptr, _tau_tmp.ptr)
    return _A_tmp, _tau_tmp

_set_types("linalg_QR_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_solve(QR, tau, b, x=None):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QR_solve(_QR_tmp.ptr, _tau_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QR_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_svx(QR, tau, x):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QR_svx(_QR_tmp.ptr, _tau_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QR_lssolve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_lssolve(QR, tau, b, x=None, residual=None):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    if residual is None:
        _residual_tmp = vector(_QR_tmp.shape[0])
        _residual_tmp.set_zero()
    else:
        _residual_tmp = _as_vector(residual)
    _res = libgsl.gsl_linalg_QR_lssolve(_QR_tmp.ptr, _tau_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr, _residual_tmp.ptr)
    return _x_tmp, _residual_tmp

_set_types("linalg_QR_QTvec", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_QTvec(QR, tau, v):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _v_tmp = _as_vector(v)
    _res = libgsl.gsl_linalg_QR_QTvec(_QR_tmp.ptr, _tau_tmp.ptr, _v_tmp.ptr)
    return _v_tmp

_set_types("linalg_QR_Qvec", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_Qvec(QR, tau, v):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _v_tmp = _as_vector(v)
    _res = libgsl.gsl_linalg_QR_Qvec(_QR_tmp.ptr, _tau_tmp.ptr, _v_tmp.ptr)
    return _v_tmp

_set_types("linalg_QR_QTmat", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_QR_QTmat(QR, tau, A):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_linalg_QR_QTmat(_QR_tmp.ptr, _tau_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("linalg_QR_Rsolve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_Rsolve(QR, b, x=None):
    _QR_tmp = _as_matrix(QR)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QR_Rsolve(_QR_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QR_Rsvx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_QR_Rsvx(QR, x):
    _QR_tmp = _as_matrix(QR)
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QR_Rsvx(_QR_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QR_unpack", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_matrix)])
def linalg_QR_unpack(QR, tau, Q=None, R=None):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    if Q is None:
        _Q_tmp = matrix(*[_QR_tmp.shape[0], _QR_tmp.shape[0]])
        _Q_tmp.set_zero()
    else:
        _Q_tmp = _as_matrix(Q)
    if R is None:
        _R_tmp = matrix(*_QR_tmp.shape)
        _R_tmp.set_zero()
    else:
        _R_tmp = _as_matrix(R)
    _res = libgsl.gsl_linalg_QR_unpack(_QR_tmp.ptr, _tau_tmp.ptr, _Q_tmp.ptr, _R_tmp.ptr)
    return _Q_tmp, _R_tmp

_set_types("linalg_QR_QRsolve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_QRsolve(Q, R, b, x=None):
    _Q_tmp = _as_matrix(Q)
    _R_tmp = _as_matrix(R)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_Q_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QR_QRsolve(_Q_tmp.ptr, _R_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QR_update", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QR_update(Q, R, w, v):
    _Q_tmp = _as_matrix(Q)
    _R_tmp = _as_matrix(R)
    _w_tmp = _as_vector(w)
    _v_tmp = _as_vector(v)
    _res = libgsl.gsl_linalg_QR_update(_Q_tmp.ptr, _R_tmp.ptr, _w_tmp.ptr, _v_tmp.ptr)
    return _Q_tmp, _R_tmp

_set_types("linalg_R_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_R_solve(R, b, x=None):
    _R_tmp = _as_matrix(R)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_R_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_R_solve(_R_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_R_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_R_svx(R, x):
    _R_tmp = _as_matrix(R)
    _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_R_svx(_R_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QRPT_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_permutation), POINTER(c_int), POINTER(gsl_vector)])
def linalg_QRPT_decomp(A, tau=None, p=None, norm=None):
    _A_tmp = _as_matrix(A)
    if tau is None:
        _tau_tmp = vector(min(*_A_tmp.shape))
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector(tau)
    p, pptr = _as_perm_dst(p, _A_tmp.shape[1])
    signum = c_int()
    if norm is None:
        _norm_tmp = vector(_A_tmp.shape[1])
        _norm_tmp.set_zero()
    else:
        _norm_tmp = _as_vector_dst(norm)
    _res = libgsl.gsl_linalg_QRPT_decomp(_A_tmp.ptr, _tau_tmp.ptr, pptr, byref(signum), _norm_tmp.ptr)
    return _A_tmp, _tau_tmp, p, signum.value

_set_types("linalg_QRPT_decomp2", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_permutation), POINTER(c_int), POINTER(gsl_vector)])
def linalg_QRPT_decomp2(A, q=None, r=None, tau=None, p=None, norm=None):
    _A_tmp = _as_matrix(A)
    if q is None:
        _q_tmp = matrix(*[_A_tmp.shape[0], _A_tmp.shape[0]])
        _q_tmp.set_zero()
    else:
        _q_tmp = _as_matrix(q)
    if r is None:
        _r_tmp = matrix(*_A_tmp.shape)
        _r_tmp.set_zero()
    else:
        _r_tmp = _as_matrix(r)
    if tau is None:
        _tau_tmp = vector(min(*_A_tmp.shape))
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector(tau)
    p, pptr = _as_perm_dst(p, _A_tmp.shape[1])
    signum = c_int()
    if norm is None:
        _norm_tmp = vector(_A_tmp.shape[1])
        _norm_tmp.set_zero()
    else:
        _norm_tmp = _as_vector_dst(norm)
    _res = libgsl.gsl_linalg_QRPT_decomp2(_A_tmp.ptr, _q_tmp.ptr, _r_tmp.ptr, _tau_tmp.ptr, pptr, byref(signum), _norm_tmp.ptr)
    return _q_tmp, _r_tmp, _tau_tmp, p, signum.value

_set_types("linalg_QRPT_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QRPT_solve(QR, tau, p, b, x=None):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QRPT_solve(_QR_tmp.ptr, _tau_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QRPT_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_permutation), POINTER(gsl_vector)])
def linalg_QRPT_svx(QR, tau, p, x=None):
    _QR_tmp = _as_matrix(QR)
    _tau_tmp = _as_vector(tau)
    if isinstance(p, permutation):
        p = p.ptr
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QRPT_svx(_QR_tmp.ptr, _tau_tmp.ptr, p, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QRPT_QRsolve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QRPT_QRsolve(Q, R, p, b, x=None):
    _Q_tmp = _as_matrix(Q)
    _R_tmp = _as_matrix(R)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_Q_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QRPT_QRsolve(_Q_tmp.ptr, _R_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QRPT_update", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QRPT_update(Q, R, p, w, v):
    _Q_tmp = _as_matrix(Q)
    _R_tmp = _as_matrix(R)
    if isinstance(p, permutation):
        p = p.ptr
    _w_tmp = _as_vector(w)
    _v_tmp = _as_vector(v)
    _res = libgsl.gsl_linalg_QRPT_update(_Q_tmp.ptr, _R_tmp.ptr, p, _w_tmp.ptr, _v_tmp.ptr)
    return _Q_tmp, _R_tmp

_set_types("linalg_QRPT_Rsolve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_QRPT_Rsolve(QR, p, b, x=None):
    _QR_tmp = _as_matrix(QR)
    if isinstance(p, permutation):
        p = p.ptr
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QRPT_Rsolve(_QR_tmp.ptr, p, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_QRPT_Rsvx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_permutation), POINTER(gsl_vector)])
def linalg_QRPT_Rsvx(QR, p, x=None):
    _QR_tmp = _as_matrix(QR)
    if isinstance(p, permutation):
        p = p.ptr
    if x is None:
        _x_tmp = vector(_QR_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_QRPT_Rsvx(_QR_tmp.ptr, p, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_SV_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_SV_decomp(A, V=None, S=None, work=None):
    _A_tmp = _as_matrix(A)
    if V is None:
        _V_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    if S is None:
        _S_tmp = vector(_A_tmp.shape[1])
        _S_tmp.set_zero()
    else:
        _S_tmp = _as_vector(S)
    if work is None:
        _work_tmp = vector(_A_tmp.shape[1])
        _work_tmp.set_zero()
    else:
        _work_tmp = _as_vector_dst(work)
    _res = libgsl.gsl_linalg_SV_decomp(_A_tmp.ptr, _V_tmp.ptr, _S_tmp.ptr, _work_tmp.ptr)
    return _A_tmp, _V_tmp, _S_tmp

_set_types("linalg_SV_decomp_mod", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_SV_decomp_mod(A, X=None, V=None, S=None, work=None):
    _A_tmp = _as_matrix(A)
    if X is None:
        _X_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _X_tmp.set_zero()
    else:
        _X_tmp = _as_matrix_dst(X)
    if V is None:
        _V_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    if S is None:
        _S_tmp = vector(_A_tmp.shape[1])
        _S_tmp.set_zero()
    else:
        _S_tmp = _as_vector(S)
    if work is None:
        _work_tmp = vector(_A_tmp.shape[1])
        _work_tmp.set_zero()
    else:
        _work_tmp = _as_vector_dst(work)
    _res = libgsl.gsl_linalg_SV_decomp_mod(_A_tmp.ptr, _X_tmp.ptr, _V_tmp.ptr, _S_tmp.ptr, _work_tmp.ptr)
    return _A_tmp, _V_tmp, _S_tmp

_set_types("linalg_SV_decomp_jacobi", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_SV_decomp_jacobi(A, V=None, S=None):
    _A_tmp = _as_matrix(A)
    if V is None:
        _V_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    if S is None:
        _S_tmp = vector(_A_tmp.shape[1])
        _S_tmp.set_zero()
    else:
        _S_tmp = _as_vector(S)
    _res = libgsl.gsl_linalg_SV_decomp_jacobi(_A_tmp.ptr, _V_tmp.ptr, _S_tmp.ptr)
    return _A_tmp, _V_tmp, _S_tmp

_set_types("linalg_SV_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_SV_solve(U, V, S, b, x=None):
    _U_tmp = _as_matrix(U)
    _V_tmp = _as_matrix(V)
    _S_tmp = _as_vector(S)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_U_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_SV_solve(_U_tmp.ptr, _V_tmp.ptr, _S_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_cholesky_decomp", _gsl_check_status, [POINTER(gsl_matrix)])
def linalg_cholesky_decomp(A):
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_linalg_cholesky_decomp(_A_tmp.ptr)
    return _A_tmp

_set_types("linalg_complex_cholesky_decomp", _gsl_check_status, [POINTER(gsl_matrix_complex)])
def linalg_complex_cholesky_decomp(A):
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_linalg_complex_cholesky_decomp(_A_tmp.ptr)
    return _A_tmp

_set_types("linalg_cholesky_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_cholesky_solve(cholesky, b, x=None):
    _cholesky_tmp = _as_matrix(cholesky)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_cholesky_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_cholesky_solve(_cholesky_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_complex_cholesky_solve", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def linalg_complex_cholesky_solve(cholesky, b, x=None):
    _cholesky_tmp = _as_matrix_complex(cholesky)
    _b_tmp = _as_vector_complex(b)
    if x is None:
        _x_tmp = vector_complex(_cholesky_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_linalg_complex_cholesky_solve(_cholesky_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_cholesky_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_cholesky_svx(cholesky, x=None):
    _cholesky_tmp = _as_matrix(cholesky)
    if x is None:
        _x_tmp = vector(_cholesky_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_cholesky_svx(_cholesky_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_complex_cholesky_svx", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex)])
def linalg_complex_cholesky_svx(cholesky, x=None):
    _cholesky_tmp = _as_matrix_complex(cholesky)
    if x is None:
        _x_tmp = vector_complex(_cholesky_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector_complex(x)
    _res = libgsl.gsl_linalg_complex_cholesky_svx(_cholesky_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_symmtd_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_symmtd_decomp(A, tau=None):
    _A_tmp = _as_matrix(A)
    if tau is None:
        _tau_tmp = vector(_A_tmp.shape[1]-1)
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector(tau)
    _res = libgsl.gsl_linalg_symmtd_decomp(_A_tmp.ptr, _tau_tmp.ptr)
    return _A_tmp, _tau_tmp

_set_types("linalg_symmtd_unpack", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_symmtd_unpack(A, tau, Q=None, diag=None, subdiag=None):
    _A_tmp = _as_matrix(A)
    _tau_tmp = _as_vector(tau)
    if Q is None:
        _Q_tmp = matrix(*_A_tmp.shape)
        _Q_tmp.set_zero()
    else:
        _Q_tmp = _as_matrix(Q)
    if diag is None:
        _diag_tmp = vector(_A_tmp.shape[1])
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if subdiag is None:
        _subdiag_tmp = vector(_A_tmp.shape[1]-1)
        _subdiag_tmp.set_zero()
    else:
        _subdiag_tmp = _as_vector(subdiag)
    _res = libgsl.gsl_linalg_symmtd_unpack(_A_tmp.ptr, _tau_tmp.ptr, _Q_tmp.ptr, _diag_tmp.ptr, _subdiag_tmp.ptr)
    return _Q_tmp, _diag_tmp, _subdiag_tmp

_set_types("linalg_symmtd_unpack_T", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_symmtd_unpack_T(A, diag=None, subdiag=None):
    _A_tmp = _as_matrix(A)
    if diag is None:
        _diag_tmp = vector(_A_tmp.shape[1])
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if subdiag is None:
        _subdiag_tmp = vector(_A_tmp.shape[1]-1)
        _subdiag_tmp.set_zero()
    else:
        _subdiag_tmp = _as_vector(subdiag)
    _res = libgsl.gsl_linalg_symmtd_unpack_T(_A_tmp.ptr, _diag_tmp.ptr, _subdiag_tmp.ptr)
    return _diag_tmp, _subdiag_tmp

_set_types("linalg_hermtd_decomp", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex)])
def linalg_hermtd_decomp(A, tau=None):
    _A_tmp = _as_matrix_complex(A)
    if tau is None:
        _tau_tmp = vector_complex(_A_tmp.shape[1]-1)
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector_complex(tau)
    _res = libgsl.gsl_linalg_hermtd_decomp(_A_tmp.ptr, _tau_tmp.ptr)
    return _A_tmp, _tau_tmp

_set_types("linalg_hermtd_unpack", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_hermtd_unpack(A, tau, Q=None, diag=None, subdiag=None):
    _A_tmp = _as_matrix_complex(A)
    _tau_tmp = _as_vector_complex(tau)
    if Q is None:
        _Q_tmp = matrix_complex(*_A_tmp.shape)
        _Q_tmp.set_zero()
    else:
        _Q_tmp = _as_matrix_complex(Q)
    if diag is None:
        _diag_tmp = vector(_A_tmp.shape[1])
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if subdiag is None:
        _subdiag_tmp = vector(_A_tmp.shape[1]-1)
        _subdiag_tmp.set_zero()
    else:
        _subdiag_tmp = _as_vector(subdiag)
    _res = libgsl.gsl_linalg_hermtd_unpack(_A_tmp.ptr, _tau_tmp.ptr, _Q_tmp.ptr, _diag_tmp.ptr, _subdiag_tmp.ptr)
    return _Q_tmp, _diag_tmp, _subdiag_tmp

_set_types("linalg_hermtd_unpack_T", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_hermtd_unpack_T(A, diag=None, subdiag=None):
    _A_tmp = _as_matrix_complex(A)
    if diag is None:
        _diag_tmp = vector(_A_tmp.shape[1])
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if subdiag is None:
        _subdiag_tmp = vector(_A_tmp.shape[1]-1)
        _subdiag_tmp.set_zero()
    else:
        _subdiag_tmp = _as_vector(subdiag)
    _res = libgsl.gsl_linalg_hermtd_unpack_T(_A_tmp.ptr, _diag_tmp.ptr, _subdiag_tmp.ptr)
    return _diag_tmp, _subdiag_tmp

_set_types("linalg_hessenberg_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_hessenberg_decomp(A, tau=None):
    _A_tmp = _as_matrix(A)
    if tau is None:
        _tau_tmp = vector(_A_tmp.shape[1])
        _tau_tmp.set_zero()
    else:
        _tau_tmp = _as_vector(tau)
    _res = libgsl.gsl_linalg_hessenberg_decomp(_A_tmp.ptr, _tau_tmp.ptr)
    return _A_tmp, _tau_tmp

_set_types("linalg_hessenberg_unpack", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_hessenberg_unpack(H, tau, U=None):
    _H_tmp = _as_matrix(H)
    _tau_tmp = _as_vector(tau)
    if U is None:
        _U_tmp = matrix(*_H_tmp.shape)
        _U_tmp.set_zero()
    else:
        _U_tmp = _as_matrix(U)
    _res = libgsl.gsl_linalg_hessenberg_unpack(_H_tmp.ptr, _tau_tmp.ptr, _U_tmp.ptr)
    return _U_tmp

_set_types("linalg_hessenberg_unpack_accum", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_hessenberg_unpack_accum(H, tau, V):
    _H_tmp = _as_matrix(H)
    _tau_tmp = _as_vector(tau)
    _V_tmp = _as_matrix(V)
    _res = libgsl.gsl_linalg_hessenberg_unpack_accum(_H_tmp.ptr, _tau_tmp.ptr, _V_tmp.ptr)
    return _V_tmp

_set_types("linalg_hessenberg_set_zero", _gsl_check_status, [POINTER(gsl_matrix)])
def linalg_hessenberg_set_zero(H):
    _H_tmp = _as_matrix(H)
    _res = libgsl.gsl_linalg_hessenberg_set_zero(_H_tmp.ptr)
    return _H_tmp

_set_types("linalg_hesstri_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_hesstri_decomp(A, B, U=None, V=None, work=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if U is None:
        _U_tmp = matrix(*_A_tmp.shape)
        _U_tmp.set_zero()
    else:
        _U_tmp = _as_matrix(U)
    if V is None:
        _V_tmp = matrix(*_A_tmp.shape)
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    if work is None:
        _work_tmp = vector(_A_tmp.shape[1])
        _work_tmp.set_zero()
    else:
        _work_tmp = _as_vector_dst(work)
    _res = libgsl.gsl_linalg_hesstri_decomp(_A_tmp.ptr, _B_tmp.ptr, _U_tmp.ptr, _V_tmp.ptr, _work_tmp.ptr)
    return _A_tmp, _B_tmp, _U_tmp, _V_tmp

_set_types("linalg_bidiag_decomp", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_bidiag_decomp(A, tau_U=None, tau_V=None):
    _A_tmp = _as_matrix(A)
    if tau_U is None:
        _tau_U_tmp = vector(min(*_A_tmp.shape))
        _tau_U_tmp.set_zero()
    else:
        _tau_U_tmp = _as_vector(tau_U)
    if tau_V is None:
        _tau_V_tmp = vector(min(*_A_tmp.shape)-1)
        _tau_V_tmp.set_zero()
    else:
        _tau_V_tmp = _as_vector(tau_V)
    _res = libgsl.gsl_linalg_bidiag_decomp(_A_tmp.ptr, _tau_U_tmp.ptr, _tau_V_tmp.ptr)
    return _A_tmp, _tau_U_tmp, _tau_V_tmp

_set_types("linalg_bidiag_unpack", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_bidiag_unpack(A, tau_U, tau_V, U=None, V=None, diag=None, superdiag=None):
    _A_tmp = _as_matrix(A)
    _tau_U_tmp = _as_vector(tau_U)
    if U is None:
        _U_tmp = matrix(*_A_tmp.shape)
        _U_tmp.set_zero()
    else:
        _U_tmp = _as_matrix(U)
    _tau_V_tmp = _as_vector(tau_V)
    if V is None:
        _V_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    if diag is None:
        _diag_tmp = vector(min(*_A_tmp.shape))
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if superdiag is None:
        _superdiag_tmp = vector(min(*_A_tmp.shape)-1)
        _superdiag_tmp.set_zero()
    else:
        _superdiag_tmp = _as_vector(superdiag)
    _res = libgsl.gsl_linalg_bidiag_unpack(_A_tmp.ptr, _tau_U_tmp.ptr, _U_tmp.ptr, _tau_V_tmp.ptr, _V_tmp.ptr, _diag_tmp.ptr, _superdiag_tmp.ptr)
    return _U_tmp, _V_tmp, _diag_tmp, _superdiag_tmp

_set_types("linalg_bidiag_unpack2", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_bidiag_unpack2(A, tau_U, tau_V, V=None):
    _A_tmp = _as_matrix(A)
    _tau_U_tmp = _as_vector(tau_U)
    _tau_V_tmp = _as_vector(tau_V)
    if V is None:
        _V_tmp = matrix(*[_A_tmp.shape[1], _A_tmp.shape[1]])
        _V_tmp.set_zero()
    else:
        _V_tmp = _as_matrix(V)
    _res = libgsl.gsl_linalg_bidiag_unpack2(_A_tmp.ptr, _tau_U_tmp.ptr, _tau_V_tmp.ptr, _V_tmp.ptr)
    return _A_tmp, _V_tmp

_set_types("linalg_bidiag_unpack_B", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_bidiag_unpack_B(A, diag=None, superdiag=None):
    _A_tmp = _as_matrix(A)
    if diag is None:
        _diag_tmp = vector(min(*_A_tmp.shape))
        _diag_tmp.set_zero()
    else:
        _diag_tmp = _as_vector(diag)
    if superdiag is None:
        _superdiag_tmp = vector(min(*_A_tmp.shape)-1)
        _superdiag_tmp.set_zero()
    else:
        _superdiag_tmp = _as_vector(superdiag)
    _res = libgsl.gsl_linalg_bidiag_unpack_B(_A_tmp.ptr, _diag_tmp.ptr, _superdiag_tmp.ptr)
    return _diag_tmp, _superdiag_tmp

_set_types("linalg_householder_transform", c_double, [POINTER(gsl_vector)])
def linalg_householder_transform(v):
    _v_tmp = _as_vector(v)
    _res = libgsl.gsl_linalg_householder_transform(_v_tmp.ptr)
    return _res, _v_tmp

_set_types("linalg_complex_householder_transform", gsl_complex, [POINTER(gsl_vector_complex)])
def linalg_complex_householder_transform(v):
    _v_tmp = _as_vector_complex(v)
    _res = libgsl.gsl_linalg_complex_householder_transform(_v_tmp.ptr)
    return _res, _v_tmp

_set_types("linalg_householder_hm", _gsl_check_status, [c_double, POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_householder_hm(tau, v, A):
    _v_tmp = _as_vector(v)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_linalg_householder_hm(tau, _v_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("linalg_complex_householder_hm", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def linalg_complex_householder_hm(tau, v, A):
    _v_tmp = _as_vector_complex(v)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_linalg_complex_householder_hm(tau, _v_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("linalg_householder_mh", _gsl_check_status, [c_double, POINTER(gsl_vector), POINTER(gsl_matrix)])
def linalg_householder_mh(tau, v, A):
    _v_tmp = _as_vector(v)
    _A_tmp = _as_matrix(A)
    _res = libgsl.gsl_linalg_householder_mh(tau, _v_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("linalg_complex_householder_mh", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex)])
def linalg_complex_householder_mh(tau, v, A):
    _v_tmp = _as_vector_complex(v)
    _A_tmp = _as_matrix_complex(A)
    _res = libgsl.gsl_linalg_complex_householder_mh(tau, _v_tmp.ptr, _A_tmp.ptr)
    return _A_tmp

_set_types("linalg_householder_hv", _gsl_check_status, [c_double, POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_householder_hv(tau, v, w):
    _v_tmp = _as_vector(v)
    _w_tmp = _as_vector(w)
    _res = libgsl.gsl_linalg_householder_hv(tau, _v_tmp.ptr, _w_tmp.ptr)
    return _w_tmp

_set_types("linalg_complex_householder_hv", _gsl_check_status, [gsl_complex, POINTER(gsl_vector_complex), POINTER(gsl_vector_complex)])
def linalg_complex_householder_hv(tau, v, w):
    _v_tmp = _as_vector_complex(v)
    _w_tmp = _as_vector_complex(w)
    _res = libgsl.gsl_linalg_complex_householder_hv(tau, _v_tmp.ptr, _w_tmp.ptr)
    return _w_tmp

_set_types("linalg_HH_solve", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_HH_solve(A, b, x=None):
    _A_tmp = _as_matrix(A)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_A_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_HH_solve(_A_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_HH_svx", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_HH_svx(A, x=None):
    _A_tmp = _as_matrix(A)
    if x is None:
        _x_tmp = vector(_A_tmp.shape[1])
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_HH_svx(_A_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_solve_tridiag", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_solve_tridiag(diag, e, f, b, x=None):
    _diag_tmp = _as_vector(diag)
    _e_tmp = _as_vector(e)
    _f_tmp = _as_vector(f)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_diag_tmp.__len__())
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_solve_tridiag(_diag_tmp.ptr, _e_tmp.ptr, _f_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_solve_symm_tridiag", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_solve_symm_tridiag(diag, e, b, x=None):
    _diag_tmp = _as_vector(diag)
    _e_tmp = _as_vector(e)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_diag_tmp.__len__())
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_solve_symm_tridiag(_diag_tmp.ptr, _e_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_solve_cyc_tridiag", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_solve_cyc_tridiag(diag, e, f, b, x=None):
    _diag_tmp = _as_vector(diag)
    _e_tmp = _as_vector(e)
    _f_tmp = _as_vector(f)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_diag_tmp.__len__())
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_solve_cyc_tridiag(_diag_tmp.ptr, _e_tmp.ptr, _f_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_solve_symm_cyc_tridiag", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector), POINTER(gsl_vector)])
def linalg_solve_symm_cyc_tridiag(diag, e, b, x=None):
    _diag_tmp = _as_vector(diag)
    _e_tmp = _as_vector(e)
    _b_tmp = _as_vector(b)
    if x is None:
        _x_tmp = vector(_diag_tmp.__len__())
        _x_tmp.set_zero()
    else:
        _x_tmp = _as_vector(x)
    _res = libgsl.gsl_linalg_solve_symm_cyc_tridiag(_diag_tmp.ptr, _e_tmp.ptr, _b_tmp.ptr, _x_tmp.ptr)
    return _x_tmp

_set_types("linalg_balance_matrix", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector)])
def linalg_balance_matrix(A, D=None):
    _A_tmp = _as_matrix(A)
    if D is None:
        _D_tmp = vector(_A_tmp.shape[1])
        _D_tmp.set_zero()
    else:
        _D_tmp = _as_vector(D)
    _res = libgsl.gsl_linalg_balance_matrix(_A_tmp.ptr, _D_tmp.ptr)
    return _A_tmp, _D_tmp

