from utils import *
from utils import _set_types, _add_function

class _gsl_complex_base(Structure):
    def __init__(self, *args):
        super(_gsl_complex_base, self).__init__()
        if len(args) > 0:
            if isinstance(args[0], complex):
                self.real = args[0].real
                self.imag = args[0].imag
            elif len(args) == 2:
                self.real = args[0]
                self.imag = args[1]
            elif isinstance(args[0], (gsl_complex, gsl_complex_float)):
                self.real = args[0].real
                self.imag = args[0].imag
            else:
                # assume args[0] is a real number
                self.real = args[0]
                self.imag = 0
    @classmethod
    def from_param(cls, x):
        if not isinstance(x, cls):
            x = cls(x)
        return x
    def __setattr__(self, name, val):
        if name == "real":
            self.dat[0] = val
        elif name == "imag":
            self.dat[1] = val
        else:
            raise AttributeError()
    def __complex__(self):
        return complex(self.real, self.imag)
    def __str__(self):
        if self.imag < 0:
            sgn = ""
        else:
            sgn = "+"
        return "(%g%s%gi)" % (self.real, sgn, self.imag)
    
class gsl_complex(_gsl_complex_base):
    _fields_ = [("dat", c_double * 2)]
    def __init__(self, *args):
        super(gsl_complex, self).__init__(*args)
    def __getattr__(self, name):
        if name == "real":
            return self.dat[0]
        elif name == "imag":
            return self.dat[1]
        elif name == "arg":
            return libgsl.gsl_complex_arg(self)
        elif name == "abs":
            return libgsl.gsl_complex_abs(self)
        elif name == "abs2":
            return libgsl.gsl_complex_abs2(self)
        elif name == "logabs":
            return libgsl.gsl_complex_logabs(self)
        else:
            raise AttributeError()

    def __add__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_add(self, other)
        if isinstance(other, complex):
            return libgsl.gsl_complex_add(self, gsl_complex(other))
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_add_real(self, other)
        return NotImplemented
    def __radd__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_add(other, self)
        if isinstance(other, (float, int, complex)):
            return libgsl.gsl_complex_add(gsl_complex(other), self)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_sub(self, other)
        if isinstance(other, complex):
            return libgsl.gsl_complex_sub(self, gsl_complex(other))
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_sub_real(self, other)
        return NotImplemented
    def __rsub__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_sub(other, self)
        if isinstance(other, (float, int, complex)):
            return libgsl.gsl_complex_sub(gsl_complex(other), self)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_mul(self, other)
        if isinstance(other, complex):
            return libgsl.gsl_complex_mul(self, gsl_complex(other))
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_mul_real(self, other)
        return NotImplemented
    def __rmul__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_mul(other, self)
        if isinstance(other, complex):
            return libgsl.gsl_complex_mul(gsl_complex(other), self)
        # changes operand order but is faster:
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_mul_real(self, other)
        return NotImplemented

    def __div__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_div(self, other)
        if isinstance(other, complex):
            return libgsl.gsl_complex_div(self, gsl_complex(other))
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_div_real(self, other)
        return NotImplemented
    def __rdiv__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_div(other, self)
        if isinstance(other, (float, int, complex)):
            return libgsl.gsl_complex_div(gsl_complex(other), self)
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_pow(self, other)
        if isinstance(other, complex):
            return libgsl.gsl_complex_pow(self, gsl_complex(other))
        if isinstance(other, (float, int)):
            return libgsl.gsl_complex_pow_real(self, other)
        return NotImplemented
    def __rpow__(self, other):
        if isinstance(other, gsl_complex):
            return libgsl.gsl_complex_pow(other, self)
        if isinstance(other, (float, int, complex)):
            return libgsl.gsl_complex_pow(gsl_complex(other), self)
        return NotImplemented

    def add_imag(self, y):
        return libgsl.gsl_complex_add_imag(self, y)
    def sub_imag(self, y):
        return libgsl.gsl_complex_sub_imag(self, y)
    def mul_imag(self, y):
        return libgsl.gsl_complex_mul_imag(self, y)
    def div_imag(self, y):
        return libgsl.gsl_complex_div_imag(self, y)

    def __abs__(self):
        return libgsl.gsl_complex_abs(self)
    def __pos__(self):
        return self
    def __neg__(self):
        return libgsl.gsl_complex_negative(self)

    def inverse(self):
        return libgsl.gsl_complex_inverse(self)

class gsl_complex_float(_gsl_complex_base):
    _fields_ = [("dat", c_float * 2)]
    def __init__(self, *args):
        super(gsl_complex_float, self).__init__(*args)
    def __getattr__(self, name):
        if name == "real":
            return self.dat[0]
        elif name == "imag":
            return self.dat[1]
        else:
            raise AttributeError()
try:
    from ctypes import c_longdouble
    class gsl_complex_long_double(_gsl_complex_base):
        _fields_ = [("dat", c_longdouble * 2)]
        def __init__(self, *args):
            super(gsl_complex_float, self).__init__(*args)
        def __getattr__(self, name):
            if name == "real":
                return self.dat[0]
            elif name == "imag":
                return self.dat[1]
            else:
                raise AttributeError()
except:
    pass

_add_function("complex_rect", gsl_complex, [c_double, c_double], globals())
_add_function("complex_polar", gsl_complex, [c_double, c_double], globals())

_complex_properties = ["complex_arg", "complex_abs", "complex_abs2", "complex_logabs"]
for f in _complex_properties:
    _add_function(f, c_double, [gsl_complex], globals())

_complex_complex_ops = ["complex_add", "complex_sub", "complex_mul", "complex_div"]
for f in _complex_complex_ops:
    _add_function(f, gsl_complex, [gsl_complex, gsl_complex], globals())

_complex_real_ops = ["complex_add_real", "complex_sub_real", "complex_mul_real",
                     "complex_div_real", "complex_add_imag", "complex_sub_imag",
                     "complex_mul_imag", "complex_div_imag"]
for f in _complex_real_ops:
    _add_function(f, gsl_complex, [gsl_complex, c_double], globals())

_complex_unary_ops = ["complex_conjugate", "complex_inverse", "complex_negative"]
for f in _complex_unary_ops:
    _add_function(f, gsl_complex, [gsl_complex], globals())

_add_function("complex_sqrt_real", gsl_complex, [c_double], globals())
_add_function("complex_pow_real", gsl_complex, [gsl_complex, c_double], globals())
_add_function("complex_log_b", gsl_complex, [gsl_complex, gsl_complex], globals())
_add_function("complex_pow", gsl_complex, [gsl_complex, gsl_complex], globals())

_unary_functions = ["complex_sqrt", "complex_pow", "complex_exp", "complex_log", "complex_log10",
                    "complex_sin", "complex_cos", "complex_sec", 
                    "complex_csc", "complex_tan", "complex_cot",
                    "complex_arcsin", "complex_arccos", "complex_arcsec", 
                    "complex_arccsc", "complex_arctan", "complex_arccot", 
                    "complex_sinh", "complex_cosh","complex_sech", 
                    "complex_csch", "complex_tanh",
                    "complex_arcsinh", "complex_arccosh", "complex_arcsech", 
                    "complex_arccsch", "complex_arctanh", "complex_arccoth"]
for f in _unary_functions:
    _add_function(f, gsl_complex, [gsl_complex])


_real_to_complex_functions = ["complex_arcsin_real", "complex_arccos_real",
                              "complex_arcsec_real", "complex_arccsc_real",
                              "complex_arccosh_real", "complex_arctanh_real"]
for f in _real_to_complex_functions:
    _add_function(f, gsl_complex, [c_double])
