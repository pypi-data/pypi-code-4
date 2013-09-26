### automatically generated, do not edit by hand

from ctypes import c_char, c_int, c_uint, c_long, c_ulong, c_short, c_ushort
from ctypes import c_float, c_double
from ctypes import POINTER
from cgsl_complex import gsl_complex, gsl_complex_float
try:
    from ctypes import c_ubyte
except:
    pass
try:
    from ctypes import c_longdouble
except:
    pass

from utils import *



class gsl_block(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_double))]
    def __len__(self):
        return self.size


class gsl_block_float(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_float))]
    def __len__(self):
        return self.size


class gsl_block_int(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_int))]
    def __len__(self):
        return self.size


class gsl_block_uint(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_uint))]
    def __len__(self):
        return self.size


class gsl_block_long(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_long))]
    def __len__(self):
        return self.size


class gsl_block_ulong(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_ulong))]
    def __len__(self):
        return self.size


class gsl_block_short(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_short))]
    def __len__(self):
        return self.size


class gsl_block_ushort(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_ushort))]
    def __len__(self):
        return self.size


class gsl_block_char(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_char))]
    def __len__(self):
        return self.size


class gsl_block_complex(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(gsl_complex))]
    def __len__(self):
        return self.size


class gsl_block_complex_float(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(gsl_complex_float))]
    def __len__(self):
        return self.size


class gsl_block_uchar(Structure):
    _fields_ = [('size', c_size_t),
                ('data', POINTER(c_ubyte))]
    def __len__(self):
        return self.size

