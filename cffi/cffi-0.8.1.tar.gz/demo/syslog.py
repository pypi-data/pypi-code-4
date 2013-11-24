import cffi

XXXXXXXXXX

ffi = cffi.FFI()
ffi.cdef("""

""")

__all__ = ALL_CONSTANTS + (
    'openlog', 'syslog', 'closelog', 'setlogmask',
    'LOG_MASK', 'LOG_UPTO')

del ALL_CONSTANTS


