from utils import *
from utils import _set_types, _add_function
from utils import _gsl_check_status, _gsl_check_null_pointer

from cgsl_complex import gsl_complex

_add_function("poly_eval", c_double, [POINTER(c_double), c_int, c_double], globals())
_set_types("poly_solve_quadratic", c_int, [c_double, c_double, c_double,
                                           POINTER(c_double), POINTER(c_double)])
_set_types("poly_complex_solve_quadratic", c_int, [c_double, c_double, c_double,
                                                   POINTER(gsl_complex), POINTER(gsl_complex)])

_set_types("poly_solve_cubic", c_int, [c_double, c_double, c_double,
                                       POINTER(c_double), POINTER(c_double), POINTER(c_double)])
_set_types("poly_complex_solve_cubic", c_int, [c_double, c_double, c_double,
                                               POINTER(gsl_complex),
                                               POINTER(gsl_complex),
                                               POINTER(gsl_complex)])

def poly_solve_quadratic(a, b, c):
    r1 = c_double()
    r2 = c_double()
    nroots = libgsl.gsl_poly_solve_quadratic(a, b, c, byref(r1), byref(r2))
    if nroots == 2:
        res = (r1.value, r2.value)
    elif nroots == 1:
        res = (r1.value,)
    else:
        res = ()
    return res
def poly_complex_solve_quadratic(a, b, c):
    r1 = gsl_complex()
    r2 = gsl_complex()
    nroots = libgsl.gsl_poly_complex_solve_quadratic(a, b, c, byref(r1), byref(r2))
    if nroots == 2:
        res = (r1, r2)
    elif nroots == 1:
        res = (r1,)
    else:
        # should never happen
        assert False
    return res
def poly_solve_cubic(a, b, c):
    r1 = c_double()
    r2 = c_double()
    r3 = c_double()
    nroots = libgsl.gsl_poly_solve_cubic(a, b, c, byref(r1), byref(r2), byref(r3))
    if nroots == 3:
        res = (r1.value, r2.value, r3.value)
    elif nroots == 1:
        res = (r1.value,)
    else:
        # should never happen
        assert False
    return res
def poly_complex_solve_cubic(a, b, c):
    r1 = gsl_complex()
    r2 = gsl_complex()
    r3 = gsl_complex()
    nroots = libgsl.gsl_poly_complex_solve_cubic(a, b, c, byref(r1), byref(r2), byref(r3))
    assert nroots == 3
    return (r1, r2, r3)

class gsl_poly_complex_workspace(Structure):
    pass

_set_types("poly_complex_workspace_alloc", POINTER(gsl_poly_complex_workspace),
           [c_size_t])
_set_types("poly_complex_workspace_free", None, [POINTER(gsl_poly_complex_workspace)])
_set_types("poly_complex_solve", _gsl_check_status,
           [POINTER(c_double), c_size_t, POINTER(gsl_poly_complex_workspace),
            POINTER(c_double)])

class poly_complex_worspace(object):
    def __init__(self, n):
        self.libgsl = libgsl
        self.ptr = libgsl.gsl_poly_complex_workspace_alloc(n)
        self.n = n
        _gsl_check_null_pointer(self.ptr)
    def __del__(self):
        self.libgsl.gsl_poly_complex_workspace_free(self.ptr)


class poly(object):
    def __init__(self, initializer):
        if isinstance(initializer, (int, long)):
            self.c = (c_double * initializer)()
        else:
            self.c = (c_double * len(initializer))(*initializer)
        self.n = len(self.c)
    def __call__(self, x):
        return libgsl.gsl_poly_eval(self.c, self.n, x)

    def __len__(self):
        return self.n
    def __getitem__(self, i):
        return self.c[i]
    def __setitem__(self, i, x):
        self.c[i] = x

    def degree(self):
        return self.n - 1

    def __repr__(self):
        return "poly([" + ", ".join([str(x) for x in self]) + "])"
    def __str__(self):
        return "".join(["%+g" % ci + "*x^%d"%i for i, ci in enumerate(self.c) if ci != 0])

    def roots(self, workspace = None):
        if self.n == 3:
            return poly_complex_solve_quadratic(self.c[2], self.c[1], self.c[0])
        elif self.n == 4:
            a0 = self.c[3]
            return poly_complex_solve_cubic(self.c[2] / a0, self.c[1] / a0, self.c[0] / a0)
        if workspace is None or workspace.n < self.n:
            workspace = poly_complex_worspace(self.n)
        z = (c_double * (2 * (self.n - 1)))()
        libgsl.gsl_poly_complex_solve(self.c, self.n, workspace.ptr, z)
        res = []
        for i in xrange(self.n - 1):
            res.append(gsl_complex(z[2*i], z[2*i + 1]))
        return res


### Divided difference polynomials

_set_types("poly_dd_init", _gsl_check_status,
           [POINTER(c_double), POINTER(c_double), POINTER(c_double), c_size_t])
_set_types("poly_dd_eval", c_double,
           [POINTER(c_double), POINTER(c_double), c_size_t, c_double])

_set_types("poly_dd_taylor", _gsl_check_status,
           [POINTER(c_double), c_double, POINTER(c_double),
            POINTER(c_double), c_size_t, POINTER(c_double)])

class poly_dd(object):
    """A polynomial in divided difference form."""
    def __init__(self, xa, ya):
        if len(xa) != len(ya):
            raise GSL_Error(GSL_EINVAL, "xa and ya arrays of differing lengths")
        self.n = len(xa)
        self.xa = (c_double * self.n)(*xa)
        self.ya = (c_double * self.n)(*ya)
        self.c  = (c_double * self.n)()
        libgsl.gsl_poly_dd_init(self.c, self.xa, self.ya, self.n)

    def __call__(self, x):
        return libgsl.gsl_poly_dd_eval(self.c, self.xa, self.n, x)

    def degree(self):
        return self.n - 1

    def taylor(self, xp):
        """Return Taylor expansion around xp."""
        taylor = poly(self.n)
        workspace = (c_double * self.n)()
        libgsl.gsl_poly_dd_taylor(taylor.c, xp, self.c, self.xa, self.n, workspace)
        return taylor
    
