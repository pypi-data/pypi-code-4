
from ctypes import c_int, c_double

from cgsl_complex import gsl_complex

from utils import *
from utils import _set_types
from utils import _gsl_check_status, _gsl_check_null_pointer

from vector import vector, gsl_vector
from vector import vector_complex, gsl_vector_complex
from matrix import matrix, gsl_matrix
from matrix import matrix_complex, gsl_matrix_complex

from blas import _as_vector, _as_vector_dst
from blas import _as_vector_complex, _as_vector_complex_dst
from blas import _as_matrix, _as_matrix_complex



GSL_EIGEN_SORT_VAL_ASC = 0
GSL_EIGEN_SORT_VAL_DESC = 1
GSL_EIGEN_SORT_ABS_ASC = 2
GSL_EIGEN_SORT_ABS_DESC = 3


class gsl_eigen_symm_workspace(Structure):
    pass
_set_types("eigen_symm_alloc", POINTER(gsl_eigen_symm_workspace), [c_size_t])
_set_types("eigen_symm_free", None, [POINTER(gsl_eigen_symm_workspace)])
class eigen_symm_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_symm_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_symm_free(self.ptr)
class gsl_eigen_symmv_workspace(Structure):
    pass
_set_types("eigen_symmv_alloc", POINTER(gsl_eigen_symmv_workspace), [c_size_t])
_set_types("eigen_symmv_free", None, [POINTER(gsl_eigen_symmv_workspace)])
class eigen_symmv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_symmv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_symmv_free(self.ptr)

class gsl_eigen_herm_workspace(Structure):
    pass
_set_types("eigen_herm_alloc", POINTER(gsl_eigen_herm_workspace), [c_size_t])
_set_types("eigen_herm_free", None, [POINTER(gsl_eigen_herm_workspace)])
class eigen_herm_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_herm_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_herm_free(self.ptr)
class gsl_eigen_hermv_workspace(Structure):
    pass
_set_types("eigen_hermv_alloc", POINTER(gsl_eigen_hermv_workspace), [c_size_t])
_set_types("eigen_hermv_free", None, [POINTER(gsl_eigen_hermv_workspace)])
class eigen_hermv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_hermv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_hermv_free(self.ptr)

class gsl_eigen_nonsymm_workspace(Structure):
    pass
_set_types("eigen_nonsymm_alloc", POINTER(gsl_eigen_nonsymm_workspace), [c_size_t])
_set_types("eigen_nonsymm_free", None, [POINTER(gsl_eigen_nonsymm_workspace)])
_set_types("eigen_nonsymm_params", None, [c_int, c_int, POINTER(gsl_eigen_nonsymm_workspace)])
class eigen_nonsymm_workspace:
    def __init__(self, n, compute_t = 0, balance = 0):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_nonsymm_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if compute_t != 0 or balance != 0:
            libgsl.gsl_eigen_nonsymm_params(compute_t, balance, self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_nonsymm_free(self.ptr)
class gsl_eigen_nonsymmv_workspace(Structure):
    pass
_set_types("eigen_nonsymmv_alloc", POINTER(gsl_eigen_nonsymmv_workspace), [c_size_t])
_set_types("eigen_nonsymmv_free", None, [POINTER(gsl_eigen_nonsymmv_workspace)])
class eigen_nonsymmv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_nonsymmv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_nonsymmv_free(self.ptr)

class gsl_eigen_gensymm_workspace(Structure):
    pass
_set_types("eigen_gensymm_alloc", POINTER(gsl_eigen_gensymm_workspace), [c_size_t])
_set_types("eigen_gensymm_free", None, [POINTER(gsl_eigen_gensymm_workspace)])
class eigen_gensymm_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_gensymm_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_gensymm_free(self.ptr)
class gsl_eigen_gensymmv_workspace(Structure):
    pass
_set_types("eigen_gensymmv_alloc", POINTER(gsl_eigen_gensymmv_workspace), [c_size_t])
_set_types("eigen_gensymmv_free", None, [POINTER(gsl_eigen_gensymmv_workspace)])
class eigen_gensymmv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_gensymmv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_gensymmv_free(self.ptr)

class gsl_eigen_genherm_workspace(Structure):
    pass
_set_types("eigen_genherm_alloc", POINTER(gsl_eigen_genherm_workspace), [c_size_t])
_set_types("eigen_genherm_free", None, [POINTER(gsl_eigen_genherm_workspace)])
class eigen_genherm_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_genherm_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_genherm_free(self.ptr)
class gsl_eigen_genhermv_workspace(Structure):
    pass
_set_types("eigen_genhermv_alloc", POINTER(gsl_eigen_genhermv_workspace), [c_size_t])
_set_types("eigen_genhermv_free", None, [POINTER(gsl_eigen_genhermv_workspace)])
class eigen_genhermv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_genhermv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_genhermv_free(self.ptr)

class gsl_eigen_gen_workspace(Structure):
    pass
_set_types("eigen_gen_alloc", POINTER(gsl_eigen_gen_workspace), [c_size_t])
_set_types("eigen_gen_free", None, [POINTER(gsl_eigen_gen_workspace)])
_set_types("eigen_gen_params", None, [c_int, c_int, c_int, POINTER(gsl_eigen_gen_workspace)])
class eigen_gen_workspace:
    def __init__(self, n, compute_s = 0, compute_t = 0, balance = 0):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_gen_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        if compute_s != 0 or compute_t != 0 or balance != 0:
            libgsl.gsl_eigen_gen_params(compute_t, balance, self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_gen_free(self.ptr)
class gsl_eigen_genv_workspace(Structure):
    pass
_set_types("eigen_genv_alloc", POINTER(gsl_eigen_genv_workspace), [c_size_t])
_set_types("eigen_genv_free", None, [POINTER(gsl_eigen_genv_workspace)])
class eigen_genv_workspace:
    def __init__(self, n):
        self.libgsl = libgsl # helper for __del__
        self.ptr = libgsl.gsl_eigen_genv_alloc(n)
        _gsl_check_null_pointer(self.ptr)
        self.size = n
    def __del__(self):
        self.libgsl.gsl_eigen_genv_free(self.ptr)

_set_types("eigen_symm", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_eigen_symm_workspace)])
def eigen_symm(A, eval=None, w=None):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    w = eigen_symm_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_symm(_A_tmp.ptr, _eval_tmp.ptr, w.ptr)
    return _eval_tmp

_set_types("eigen_symmv", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_eigen_symmv_workspace)])
def eigen_symmv(A, eval=None, evec=None, w=None):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    if evec is None:
        _evec_tmp = matrix(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix(evec)
    w = eigen_symmv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_symmv(_A_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp

_set_types("eigen_herm", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_eigen_herm_workspace)])
def eigen_herm(A, eval=None, w=None):
    _A_tmp = _as_matrix_complex(A)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    w = eigen_herm_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_herm(_A_tmp.ptr, _eval_tmp.ptr, w.ptr)
    return _eval_tmp

_set_types("eigen_hermv", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_matrix_complex), POINTER(gsl_eigen_hermv_workspace)])
def eigen_hermv(A, eval=None, evec=None, w=None):
    _A_tmp = _as_matrix_complex(A)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    w = eigen_hermv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_hermv(_A_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp

_set_types("eigen_nonsymm", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_eigen_nonsymm_workspace), c_int, c_int])
def eigen_nonsymm(A, eval=None, w=None, compute_t=0, balance=0):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector_complex(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector_complex(eval)
    w = eigen_nonsymm_workspace(_A_tmp.shape[1], compute_t, balance)
    _res = libgsl.gsl_eigen_nonsymm(_A_tmp.ptr, _eval_tmp.ptr, w.ptr, compute_t, balance)
    return _eval_tmp

_set_types("eigen_nonsymm_Z", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_matrix), POINTER(gsl_eigen_nonsymm_workspace), c_int, c_int])
def eigen_nonsymm_Z(A, eval=None, Z=None, w=None, compute_t=0, balance=0):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector_complex(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector_complex(eval)
    if Z is None:
        _Z_tmp = matrix(*_A_tmp.shape)
        _Z_tmp.set_zero()
    else:
        _Z_tmp = _as_matrix(Z)
    w = eigen_nonsymm_workspace(_A_tmp.shape[1], compute_t, balance)
    _res = libgsl.gsl_eigen_nonsymm_Z(_A_tmp.ptr, _eval_tmp.ptr, _Z_tmp.ptr, w.ptr, compute_t, balance)
    return _eval_tmp, _Z_tmp

_set_types("eigen_nonsymmv", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex), POINTER(gsl_eigen_nonsymmv_workspace)])
def eigen_nonsymmv(A, eval=None, evec=None, w=None):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector_complex(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector_complex(eval)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    w = eigen_nonsymmv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_nonsymmv(_A_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp

_set_types("eigen_nonsymmv_Z", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex), POINTER(gsl_matrix), POINTER(gsl_eigen_nonsymmv_workspace)])
def eigen_nonsymmv_Z(A, eval=None, evec=None, Z=None, w=None):
    _A_tmp = _as_matrix(A)
    if eval is None:
        _eval_tmp = vector_complex(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector_complex(eval)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    if Z is None:
        _Z_tmp = matrix(*_A_tmp.shape)
        _Z_tmp.set_zero()
    else:
        _Z_tmp = _as_matrix(Z)
    w = eigen_nonsymmv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_nonsymmv_Z(_A_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, _Z_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp, _Z_tmp

_set_types("eigen_gensymm", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_eigen_gensymm_workspace)])
def eigen_gensymm(A, B, eval=None, w=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    w = eigen_gensymm_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_gensymm(_A_tmp.ptr, _B_tmp.ptr, _eval_tmp.ptr, w.ptr)
    return _eval_tmp

_set_types("eigen_gensymmv", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_eigen_gensymmv_workspace)])
def eigen_gensymmv(A, B, eval=None, evec=None, w=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    if evec is None:
        _evec_tmp = matrix(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix(evec)
    w = eigen_gensymmv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_gensymmv(_A_tmp.ptr, _B_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp

_set_types("eigen_genherm", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_eigen_genherm_workspace)])
def eigen_genherm(A, B, eval=None, w=None):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    w = eigen_genherm_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_genherm(_A_tmp.ptr, _B_tmp.ptr, _eval_tmp.ptr, w.ptr)
    return _eval_tmp

_set_types("eigen_genhermv", _gsl_check_status, [POINTER(gsl_matrix_complex), POINTER(gsl_matrix_complex), POINTER(gsl_vector), POINTER(gsl_matrix_complex), POINTER(gsl_eigen_genhermv_workspace)])
def eigen_genhermv(A, B, eval=None, evec=None, w=None):
    _A_tmp = _as_matrix_complex(A)
    _B_tmp = _as_matrix_complex(B)
    if eval is None:
        _eval_tmp = vector(_A_tmp.shape[1])
        _eval_tmp.set_zero()
    else:
        _eval_tmp = _as_vector(eval)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    w = eigen_genhermv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_genhermv(_A_tmp.ptr, _B_tmp.ptr, _eval_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _eval_tmp, _evec_tmp

_set_types("eigen_gen", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_vector), POINTER(gsl_eigen_gen_workspace), c_int, c_int, c_int])
def eigen_gen(A, B, alpha=None, beta=None, w=None, compute_t=0, compute_s=0, balance=0):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if alpha is None:
        _alpha_tmp = vector_complex(_A_tmp.shape[1])
        _alpha_tmp.set_zero()
    else:
        _alpha_tmp = _as_vector_complex(alpha)
    if beta is None:
        _beta_tmp = vector(_A_tmp.shape[1])
        _beta_tmp.set_zero()
    else:
        _beta_tmp = _as_vector(beta)
    w = eigen_gen_workspace(_A_tmp.shape[1], compute_t, compute_s, balance)
    _res = libgsl.gsl_eigen_gen(_A_tmp.ptr, _B_tmp.ptr, _alpha_tmp.ptr, _beta_tmp.ptr, w.ptr, compute_t, compute_s, balance)
    return _alpha_tmp, _beta_tmp

_set_types("eigen_gen_QZ", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_vector), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_eigen_gen_workspace), c_int, c_int, c_int])
def eigen_gen_QZ(A, B, alpha=None, beta=None, Q=None, Z=None, w=None, compute_s=0, compute_t=0, balance=0):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if alpha is None:
        _alpha_tmp = vector_complex(_A_tmp.shape[1])
        _alpha_tmp.set_zero()
    else:
        _alpha_tmp = _as_vector_complex(alpha)
    if beta is None:
        _beta_tmp = vector(_A_tmp.shape[1])
        _beta_tmp.set_zero()
    else:
        _beta_tmp = _as_vector(beta)
    if Q is None:
        _Q_tmp = matrix(*_A_tmp.shape)
        _Q_tmp.set_zero()
    else:
        _Q_tmp = _as_matrix(Q)
    if Z is None:
        _Z_tmp = matrix(*_A_tmp.shape)
        _Z_tmp.set_zero()
    else:
        _Z_tmp = _as_matrix(Z)
    w = eigen_gen_workspace(_A_tmp.shape[1], compute_s, compute_t, balance)
    _res = libgsl.gsl_eigen_gen_QZ(_A_tmp.ptr, _B_tmp.ptr, _alpha_tmp.ptr, _beta_tmp.ptr, _Q_tmp.ptr, _Z_tmp.ptr, w.ptr, compute_s, compute_t, balance)
    return _alpha_tmp, _beta_tmp, _Q_tmp, _Z_tmp

_set_types("eigen_genv", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_vector), POINTER(gsl_matrix_complex), POINTER(gsl_eigen_genv_workspace)])
def eigen_genv(A, B, alpha=None, beta=None, evec=None, w=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if alpha is None:
        _alpha_tmp = vector_complex(_A_tmp.shape[1])
        _alpha_tmp.set_zero()
    else:
        _alpha_tmp = _as_vector_complex(alpha)
    if beta is None:
        _beta_tmp = vector(_A_tmp.shape[1])
        _beta_tmp.set_zero()
    else:
        _beta_tmp = _as_vector(beta)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    w = eigen_genv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_genv(_A_tmp.ptr, _B_tmp.ptr, _alpha_tmp.ptr, _beta_tmp.ptr, _evec_tmp.ptr, w.ptr)
    return _alpha_tmp, _beta_tmp, _evec_tmp

_set_types("eigen_genv_QZ", _gsl_check_status, [POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_vector_complex), POINTER(gsl_vector), POINTER(gsl_matrix_complex), POINTER(gsl_matrix), POINTER(gsl_matrix), POINTER(gsl_eigen_genv_workspace)])
def eigen_genv_QZ(A, B, alpha=None, beta=None, evec=None, Q=None, Z=None, w=None):
    _A_tmp = _as_matrix(A)
    _B_tmp = _as_matrix(B)
    if alpha is None:
        _alpha_tmp = vector_complex(_A_tmp.shape[1])
        _alpha_tmp.set_zero()
    else:
        _alpha_tmp = _as_vector_complex(alpha)
    if beta is None:
        _beta_tmp = vector(_A_tmp.shape[1])
        _beta_tmp.set_zero()
    else:
        _beta_tmp = _as_vector(beta)
    if evec is None:
        _evec_tmp = matrix_complex(*_A_tmp.shape)
        _evec_tmp.set_zero()
    else:
        _evec_tmp = _as_matrix_complex(evec)
    if Q is None:
        _Q_tmp = matrix(*_A_tmp.shape)
        _Q_tmp.set_zero()
    else:
        _Q_tmp = _as_matrix(Q)
    if Z is None:
        _Z_tmp = matrix(*_A_tmp.shape)
        _Z_tmp.set_zero()
    else:
        _Z_tmp = _as_matrix(Z)
    w = eigen_genv_workspace(_A_tmp.shape[1])
    _res = libgsl.gsl_eigen_genv_QZ(_A_tmp.ptr, _B_tmp.ptr, _alpha_tmp.ptr, _beta_tmp.ptr, _evec_tmp.ptr, _Q_tmp.ptr, _Z_tmp.ptr, w.ptr)
    return _alpha_tmp, _beta_tmp, _evec_tmp, _Q_tmp, _Z_tmp

_set_types("eigen_symmv_sort", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_matrix), c_int])
def eigen_symmv_sort(eval, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _eval_tmp = _as_vector(eval)
    _evec_tmp = _as_matrix(evec)
    _res = libgsl.gsl_eigen_symmv_sort(_eval_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _eval_tmp, _evec_tmp

_set_types("eigen_hermv_sort", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_matrix_complex), c_int])
def eigen_hermv_sort(eval, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _eval_tmp = _as_vector(eval)
    _evec_tmp = _as_matrix_complex(evec)
    _res = libgsl.gsl_eigen_hermv_sort(_eval_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _eval_tmp, _evec_tmp

_set_types("eigen_nonsymmv_sort", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_matrix_complex), c_int])
def eigen_nonsymmv_sort(eval, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _eval_tmp = _as_vector_complex(eval)
    _evec_tmp = _as_matrix_complex(evec)
    _res = libgsl.gsl_eigen_nonsymmv_sort(_eval_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _eval_tmp, _evec_tmp

_set_types("eigen_gensymmv_sort", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_matrix), c_int])
def eigen_gensymmv_sort(eval, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _eval_tmp = _as_vector(eval)
    _evec_tmp = _as_matrix(evec)
    _res = libgsl.gsl_eigen_gensymmv_sort(_eval_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _eval_tmp, _evec_tmp

_set_types("eigen_genhermv_sort", _gsl_check_status, [POINTER(gsl_vector), POINTER(gsl_matrix_complex), c_int])
def eigen_genhermv_sort(eval, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _eval_tmp = _as_vector(eval)
    _evec_tmp = _as_matrix_complex(evec)
    _res = libgsl.gsl_eigen_genhermv_sort(_eval_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _eval_tmp, _evec_tmp

_set_types("eigen_genv_sort", _gsl_check_status, [POINTER(gsl_vector_complex), POINTER(gsl_vector), POINTER(gsl_matrix_complex), c_int])
def eigen_genv_sort(alpha, beta, evec, sort_type=GSL_EIGEN_SORT_ABS_DESC):
    _alpha_tmp = _as_vector_complex(alpha)
    _beta_tmp = _as_vector(beta)
    _evec_tmp = _as_matrix_complex(evec)
    _res = libgsl.gsl_eigen_genv_sort(_alpha_tmp.ptr, _beta_tmp.ptr, _evec_tmp.ptr, sort_type)
    return _alpha_tmp, _beta_tmp, _evec_tmp

