from utils import *
from utils import _set_types, _add_function
from utils import _int_to_bool



##### CONSTANTS
GSL_POSINF = float('inf')
GSL_NEGINF = float('-inf')
GSL_NAN = float('nan')


M_E        = 2.71828182845904523536028747135      # e
M_LOG2E    = 1.44269504088896340735992468100      # log_2 (e)
M_LOG10E   = 0.43429448190325182765112891892      # log_10 (e)
M_SQRT2    = 1.41421356237309504880168872421      # sqrt(2)
M_SQRT1_2  = 0.70710678118654752440084436210      # sqrt(1/2)
M_SQRT3    = 1.73205080756887729352744634151      # sqrt(3)
M_PI       = 3.14159265358979323846264338328      # pi
M_PI_2     = 1.57079632679489661923132169164      # pi/2
M_PI_4     = 0.78539816339744830966156608458      # pi/4
M_SQRTPI   = 1.77245385090551602729816748334      # sqrt(pi)
M_2_SQRTPI = 1.12837916709551257389615890312      # 2/sqrt(pi)
M_1_PI     = 0.31830988618379067153776752675      # 1/pi
M_2_PI     = 0.63661977236758134307553505349      # 2/pi
M_LN10     = 2.30258509299404568401799145468      # ln(10)
M_LN2      = 0.69314718055994530941723212146      # ln(2)
M_LNPI     = 1.14472988584940017414342735135      # ln(pi)
M_EULER    = 0.57721566490153286060651209008      # Euler constant



# MATEHMEATICAL FUNCTIONS

# infnities and nans
_add_function("isnan", _int_to_bool, [c_double])
_add_function("isinf", _int_to_bool, [c_double])
_add_function("finite", _int_to_bool, [c_double])
# elementary functions
_add_function("log1p", c_double, [c_double])
_add_function("expm1", c_double, [c_double])
_add_function("hypot", c_double, [c_double, c_double])
_add_function("acosh", c_double, [c_double])
_add_function("asinh", c_double, [c_double])
_add_function("atanh", c_double, [c_double])
_add_function("ldexp", c_double, [c_double, c_int])
_set_types("frexp", c_double, [c_double, POINTER(c_int)])
def frexp(x):
    e = c_int()
    y = libgsl.gsl_frexp(x, byref(e))
    return y, e.value
def GSL_SIGN(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
def GSL_IS_ODD(n):
    return n % 2 == 1
def GSL_IS_EVEN(n):
    return n % 2 == 0
# small integer powers
_add_function("pow_int", c_double, [c_double, c_int])
for e in range(2, 10):
    _add_function("pow_" + str(e), c_double, [c_double])
# approx. floating comparisons
_add_function("fcmp", _int_to_bool, [c_double, c_double, c_double])
