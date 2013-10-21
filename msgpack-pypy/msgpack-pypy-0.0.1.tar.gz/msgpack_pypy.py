"""
This is only a proof of concept for now. Use it at your own risk.

It requires msgpack-python >= 0.4

If you use the fast_cffi_list_init of PyPy, serializations of int/float lists
is 8x faster than the plain msgpack.
"""

import msgpack
if msgpack.version < (0, 4):
    raise ImportError("msgpack-pypy requires msgpack >= 0.4.0")

try:
    import __pypy__
except ImportError:
    is_pypy = False
else:
    is_pypy = True

INT_LIST = 0
FLOAT_LIST = 1

if is_pypy:
    # PyPy version, with a fast-path to pack int/float lists
    import cffi
    ffi = cffi.FFI()
    LONG_SIZE = ffi.sizeof("long")
    DOUBLE_SIZE = ffi.sizeof("double")

    # packing
    def pack(o, stream, **kwargs):
        packer = Packer(**kwargs)
        stream.write(packer.pack(o))

    def packb(o, **kwargs):
        return Packer(**kwargs).pack(o)

    class Packer(msgpack.Packer):
        def _pack(self, obj, *args):
            if isinstance(obj, list):
                strategy = __pypy__.list_strategy(obj)
                if strategy == 'int':
                    # super-fast conversion from list-of-ints to a raw
                    # buffer, only in the pypy fast_cffi_list_init branch for
                    # now
                    buf = ffi.buffer(ffi.new("long[]", obj))
                    # this extra copy should not be needed :-(
                    return self.pack_ext_type(INT_LIST, buf[:])
                elif strategy == 'float':
                    # same as above
                    buf = ffi.buffer(ffi.new("double[]", obj))
                    return self.pack_ext_type(FLOAT_LIST, buf[:])
            return msgpack.Packer._pack(self, obj, *args)

    # unpacking
    def unpack_ext_type(typecode, data):
        if typecode == INT_LIST:
            N = len(data)/LONG_SIZE
            chars = ffi.new("char[]", data)
            ints = ffi.cast("long[%d]" % N, chars)
            return list(ints)
        elif typecode == FLOAT_LIST:
            N = len(data)/DOUBLE_SIZE
            chars = ffi.new("char[]", data)
            floats = ffi.cast("double[%d]" % N, chars)
            return list(floats)
        else:
            msgpack.Unpacker.read_extended_type(self, typecode, data)


else:
    # CPython version: it does
    import array
    from msgpack import pack, packb

    def unpack_ext_type(typecode, data):
        if typecode == INT_LIST:
            ints = array.array('l')
            ints.fromstring(data)
            return list(ints)
        if typecode == FLOAT_LIST:
            floats = array.array('d')
            floats.fromstring(data)
            return list(floats)
        else:
            raise NotImplementedError("Cannot decode ext type with typecode=%d" % typecode)


def unpack(stream, **kwargs):
    return msgpack.unpack(stream, ext_hook=unpack_ext_type, **kwargs)

def unpackb(packed, **kwargs):
    return msgpack.unpackb(packed, ext_hook=unpack_ext_type, **kwargs)

# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb
