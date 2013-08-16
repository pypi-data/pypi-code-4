import struct
import _exceptions

USHORT = ">H"
SHORT = ">h"

def get_ushort(stream, offset=0):
    size = struct.calcsize(USHORT)
    data = struct.unpack_from(USHORT, stream, offset)[0]  # It will only be a single value

    return (size + offset, data)

def convert_ushort_to_short(from_format, to_format, *args):
    tmp = struct.pack(from_format, *args)
    return struct.unpack(to_format, tmp)

def skip_ushort(stream, count, offset=0):
    size = struct.calcsize(USHORT) * count

    return size + offset

def validate_ushort_is_any(stream, expected, offset=0):
    offset, value = get_ushort(stream, offset)

    if not value in expected:
        raise _exceptions.InvalidFileTypeError()

    return offset, value
